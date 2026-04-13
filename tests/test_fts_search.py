from pathlib import Path

from side_rag.db import connect_db, initialize_db
from side_rag.indexer.processor import ingest_jsonl
from side_rag.retrieval.fts import search_fts


def test_fts_search_returns_matching_chunk(tmp_path: Path) -> None:
    db_path = tmp_path / "sidecar.db"
    conn = connect_db(db_path)
    initialize_db(conn)
    fixture = Path("tests/fixtures/codex_session_sample.jsonl")

    ingest_jsonl(conn, fixture, project_id="sample_project")
    rows = search_fts(conn, "awaiting_captcha", limit=5, project_id="sample_project")

    assert rows
    assert any("awaiting_captcha" in row["content"] for row in rows)


def test_fts_search_sanitizes_natural_language_query(tmp_path: Path) -> None:
    db_path = tmp_path / "sidecar.db"
    conn = connect_db(db_path)
    initialize_db(conn)
    fixture = Path("tests/fixtures/codex_session_sample.jsonl")

    ingest_jsonl(conn, fixture, project_id="sample_project")
    rows = search_fts(
        conn,
        "Qual foi a decisao sobre CAPTCHA no SIGEF e estado awaiting_captcha?",
        limit=5,
        project_id="sample_project",
    )

    assert rows
    assert any("awaiting_captcha" in row["content"] for row in rows)
