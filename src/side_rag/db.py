from __future__ import annotations

import sqlite3
from pathlib import Path

FTS_COLUMNS = (
    "chunk_id",
    "project_id",
    "session_id",
    "source_path",
    "source_event_type",
    "role",
    "content",
)


def connect_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _current_fts_columns(conn: sqlite3.Connection) -> list[str]:
    table_exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'chunks_fts'"
    ).fetchone()
    if not table_exists:
        return []
    rows = conn.execute("PRAGMA table_info(chunks_fts)").fetchall()
    return [row["name"] for row in rows]


def _rebuild_fts(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM chunks_fts")
    conn.execute(
        """
        INSERT INTO chunks_fts (
            chunk_id, project_id, session_id, source_path, source_event_type, role, content
        )
        SELECT
            chunk_id, project_id, session_id, source_path, source_event_type, role, content
        FROM chunks
        """
    )


def _needs_fts_rebuild(conn: sqlite3.Connection) -> bool:
    chunk_count = conn.execute("SELECT COUNT(*) AS total FROM chunks").fetchone()["total"]
    fts_count = conn.execute("SELECT COUNT(*) AS total FROM chunks_fts").fetchone()["total"]
    return chunk_count != fts_count


def initialize_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            content TEXT NOT NULL,
            source_hash TEXT NOT NULL UNIQUE,
            source_path TEXT NOT NULL,
            source_event_type TEXT NOT NULL,
            source_line_start INTEGER NOT NULL,
            source_line_end INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            role TEXT NOT NULL,
            phase TEXT NOT NULL,
            prompt_number INTEGER,
            raw_chunk_id TEXT,
            parser_version TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    if _current_fts_columns(conn) != list(FTS_COLUMNS):
        conn.execute("DROP TABLE IF EXISTS chunks_fts")
        conn.execute(
            """
            CREATE VIRTUAL TABLE chunks_fts
            USING fts5(
                chunk_id UNINDEXED,
                project_id UNINDEXED,
                session_id,
                source_path,
                source_event_type,
                role,
                content
            )
            """
        )
        _rebuild_fts(conn)
    elif _needs_fts_rebuild(conn):
        _rebuild_fts(conn)

    conn.commit()
