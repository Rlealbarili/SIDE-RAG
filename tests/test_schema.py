import pytest

from side_rag.schema import ChunkModel


def test_chunk_model_requires_core_fields() -> None:
    chunk = ChunkModel(
        chunk_id="c1",
        project_id="p1",
        session_id="s1",
        content="hello",
        source_hash="hash",
        source_path="/tmp/file.jsonl",
        source_event_type="message",
        source_line_start=1,
        source_line_end=1,
        timestamp="2026-04-13T00:00:00Z",
        parser_version="0.1.0",
        created_at="2026-04-13T00:00:00Z",
    )
    assert chunk.role == "unknown"


def test_chunk_model_rejects_missing_required_fields() -> None:
    with pytest.raises(Exception):
        ChunkModel(
            chunk_id="c1",
            project_id="p1",
            session_id="s1",
            content="hello",
            source_hash="hash",
            source_path="/tmp/file.jsonl",
            source_event_type="message",
            source_line_start=1,
            source_line_end=1,
            timestamp="2026-04-13T00:00:00Z",
            parser_version="0.1.0",
        )
