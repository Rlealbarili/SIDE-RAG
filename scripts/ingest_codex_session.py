#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from side_rag.config import settings
from side_rag.db import connect_db, initialize_db
from side_rag.indexer.processor import ingest_jsonl
from side_rag.parsers.codex_parser import resolve_codex_session_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest a Codex JSONL transcript into SIDE-RAG.")
    parser.add_argument("--input", default=None, help="Path to a JSONL transcript.")
    parser.add_argument("--codex-session-id", default=None, help="Resolve a real Codex rollout by session id.")
    parser.add_argument(
        "--latest-codex-session",
        action="store_true",
        help="Resolve the latest rollout under SIDE_RAG_CODEX_SESSIONS_DIR.",
    )
    parser.add_argument("--project", required=True, help="Logical project id.")
    parser.add_argument("--session-id", default=None, help="Optional explicit session id override.")
    parser.add_argument("--dry-run", action="store_true", help="Parse without writing to SQLite.")
    args = parser.parse_args()

    if not args.input and not args.codex_session_id and not args.latest_codex_session:
        raise SystemExit("Provide --input, --codex-session-id, or --latest-codex-session")

    if sum(bool(option) for option in [args.input, args.codex_session_id, args.latest_codex_session]) > 1:
        raise SystemExit("Choose only one source selector: --input, --codex-session-id, or --latest-codex-session")

    if args.input:
        input_path = Path(args.input).expanduser().resolve()
    else:
        input_path = resolve_codex_session_file(
            session_id=args.codex_session_id,
            latest=args.latest_codex_session,
            root=settings.codex_sessions_dir,
        ).resolve()

    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    conn = connect_db(settings.db_path)
    initialize_db(conn)
    result = ingest_jsonl(
        conn=conn,
        input_path=input_path,
        project_id=args.project,
        explicit_session_id=args.session_id,
        dry_run=args.dry_run,
    )
    print(result)


if __name__ == "__main__":
    main()
