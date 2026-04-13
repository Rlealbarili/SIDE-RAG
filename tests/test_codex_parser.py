from pathlib import Path

from side_rag.parsers.codex_parser import extract_chunks


def test_extract_chunks_reads_fixture() -> None:
    fixture = Path("tests/fixtures/codex_session_sample.jsonl")
    chunks = extract_chunks(fixture, project_id="sample_project")
    assert len(chunks) == 3
    assert chunks[0].project_id == "sample_project"
    assert chunks[0].source_line_start == 1


def test_extract_chunks_handles_invalid_json_without_crashing(tmp_path: Path) -> None:
    fixture = tmp_path / "invalid.jsonl"
    fixture.write_text('{"type":"message","content":"ok"}\nnot-json\n', encoding="utf-8")

    chunks = extract_chunks(fixture, project_id="sample_project")

    assert len(chunks) == 2
    assert chunks[1].source_event_type == "raw_text"
    assert chunks[1].source_line_start == 2
    assert chunks[1].content == "not-json"


def test_extract_chunks_filters_ignored_events_and_splits_large_content(tmp_path: Path) -> None:
    fixture = tmp_path / "mixed.jsonl"
    fixture.write_text(
        "\n".join(
            [
                '{"type":"token_count","content":"ignore me"}',
                '{"type":"agent_answer","content":"alpha beta gamma delta epsilon zeta"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    chunks = extract_chunks(
        fixture,
        project_id="sample_project",
        max_chunk_chars=16,
        ignored_event_types={"token_count"},
    )

    assert len(chunks) >= 2
    assert all(chunk.source_event_type != "token_count" for chunk in chunks)
    assert all(len(chunk.content) <= 16 for chunk in chunks)
