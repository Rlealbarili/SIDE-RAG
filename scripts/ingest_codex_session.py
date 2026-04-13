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


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest a Codex JSONL transcript into SIDE-RAG.")
    parser.add_argument("--input", required=True, help="Path to a JSONL transcript.")
    parser.add_argument("--project", required=True, help="Logical project id.")
    parser.add_argument("--session-id", default=None, help="Optional explicit session id override.")
    parser.add_argument("--dry-run", action="store_true", help="Parse without writing to SQLite.")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
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
