from __future__ import annotations

import sqlite3
from pathlib import Path

from side_rag.parsers.codex_parser import extract_chunks


def upsert_chunk(conn: sqlite3.Connection, chunk: dict) -> None:
    existing = conn.execute(
        "SELECT chunk_id FROM chunks WHERE source_hash = ?",
        (chunk["source_hash"],),
    ).fetchone()

    if existing:
        conn.execute("DELETE FROM chunks WHERE source_hash = ?", (chunk["source_hash"],))
        conn.execute("DELETE FROM chunks_fts WHERE chunk_id = ?", (existing["chunk_id"],))

    conn.execute(
        """
        INSERT INTO chunks (
            chunk_id, project_id, session_id, content, source_hash, source_path,
            source_event_type, source_line_start, source_line_end, timestamp, role,
            phase, prompt_number, raw_chunk_id, parser_version, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            chunk["chunk_id"],
            chunk["project_id"],
            chunk["session_id"],
            chunk["content"],
            chunk["source_hash"],
            chunk["source_path"],
            chunk["source_event_type"],
            chunk["source_line_start"],
            chunk["source_line_end"],
            chunk["timestamp"],
            chunk["role"],
            chunk["phase"],
            chunk["prompt_number"],
            chunk["raw_chunk_id"],
            chunk["parser_version"],
            chunk["created_at"],
        ),
    )
    conn.execute(
        """
        INSERT INTO chunks_fts (
            chunk_id, project_id, session_id, source_path, source_event_type, role, content
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            chunk["chunk_id"],
            chunk["project_id"],
            chunk["session_id"],
            chunk["source_path"],
            chunk["source_event_type"],
            chunk["role"],
            chunk["content"],
        ),
    )


def ingest_jsonl(
    conn: sqlite3.Connection,
    input_path: Path,
    project_id: str | None,
    explicit_session_id: str | None = None,
    dry_run: bool = False,
) -> dict:
    chunks = extract_chunks(input_path, project_id=project_id, explicit_session_id=explicit_session_id)
    resolved_project_id = chunks[0].project_id if chunks else (project_id or "unknown")
    if dry_run:
        return {
            "mode": "dry-run",
            "input": str(input_path),
            "project_id": resolved_project_id,
            "chunks_parsed": len(chunks),
        }

    for chunk in chunks:
        upsert_chunk(conn, chunk.model_dump())
    conn.commit()

    return {
        "mode": "write",
        "input": str(input_path),
        "project_id": resolved_project_id,
        "chunks_written": len(chunks),
    }
