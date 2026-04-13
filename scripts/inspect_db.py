#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from side_rag.config import settings
from side_rag.db import connect_db, initialize_db


def main() -> None:
    conn = connect_db(settings.db_path)
    initialize_db(conn)
    row = conn.execute("SELECT COUNT(*) AS total FROM chunks").fetchone()
    print({"db_path": str(settings.db_path), "chunks": row["total"]})


if __name__ == "__main__":
    main()
