#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from side_rag.config import settings
from side_rag.db import connect_db, initialize_db
from side_rag.indexer.processor import ingest_jsonl
from side_rag.parsers.codex_parser import iter_jsonl_events, list_codex_session_files


def _session_cwd(path: Path) -> str | None:
    for _, event in iter_jsonl_events(path):
        if event.get("type") != "session_meta":
            continue
        payload = event.get("payload")
        if isinstance(payload, dict) and isinstance(payload.get("cwd"), str):
            return payload["cwd"]
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch-ingest Codex JSONL rollouts into SIDE-RAG.")
    parser.add_argument(
        "--project",
        default="auto",
        help="Logical project id. Use 'auto' (default) to infer per transcript from cwd metadata.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of rollouts to ingest, newest first. Use 0 to ingest all.",
    )
    parser.add_argument(
        "--cwd-prefix",
        default=None,
        help="Only ingest sessions whose session_meta cwd starts with this prefix.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Parse without writing to SQLite.")
    args = parser.parse_args()

    sessions = sorted(list_codex_session_files(settings.codex_sessions_dir), key=lambda path: path.stat().st_mtime, reverse=True)
    if args.cwd_prefix:
        sessions = [path for path in sessions if (_session_cwd(path) or "").startswith(args.cwd_prefix)]
    if args.limit and args.limit > 0:
        sessions = sessions[: args.limit]

    conn = connect_db(settings.db_path)
    initialize_db(conn)

    processed: list[dict[str, object]] = []
    skipped: list[dict[str, str]] = []
    for path in sessions:
        try:
            result = ingest_jsonl(
                conn=conn,
                input_path=path,
                project_id=args.project,
                explicit_session_id=None,
                dry_run=args.dry_run,
            )
            processed.append(result)
        except Exception as exc:  # pragma: no cover - defensive batch reporting
            skipped.append({"input": str(path), "error": str(exc)})

    print(
        json.dumps(
            {
                "mode": "dry-run" if args.dry_run else "write",
                "requested_limit": args.limit,
                "cwd_prefix": args.cwd_prefix,
                "sessions_selected": len(sessions),
                "processed": processed,
                "skipped": skipped,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
