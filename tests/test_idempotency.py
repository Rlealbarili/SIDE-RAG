from pathlib import Path

from side_rag.db import connect_db, initialize_db
from side_rag.indexer.processor import ingest_jsonl


def test_ingest_is_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "sidecar.db"
    conn = connect_db(db_path)
    initialize_db(conn)
    fixture = Path("tests/fixtures/codex_session_sample.jsonl")

    ingest_jsonl(conn, fixture, project_id="sample_project")
    ingest_jsonl(conn, fixture, project_id="sample_project")

    row = conn.execute("SELECT COUNT(*) AS total FROM chunks").fetchone()
    assert row["total"] == 3
