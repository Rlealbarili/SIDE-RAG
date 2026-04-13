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
from side_rag.retrieval.fts import search_fts


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a quick lexical search against SIDE-RAG.")
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--project", default=None)
    args = parser.parse_args()

    conn = connect_db(settings.db_path)
    initialize_db(conn)
    rows = search_fts(conn, args.query, limit=args.limit, project_id=args.project)
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
