from pathlib import Path

from side_rag.parsers.codex_parser import extract_chunks, resolve_codex_session_file


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


def test_extract_chunks_reads_realistic_codex_rollout_fixture() -> None:
    fixture = Path("tests/fixtures/codex_rollout_sample.jsonl")
    chunks = extract_chunks(fixture, project_id="side-rag")

    assert len(chunks) == 5
    assert chunks[0].session_id == "019d7de2-8c24-7d02-bb46-73d8f5f76aef"
    assert {chunk.source_event_type for chunk in chunks} == {
        "user_message",
        "agent_message",
        "exec_command_end",
        "patch_apply_end",
        "mcp_tool_call_end",
    }


def test_extract_chunks_sanitizes_exec_command_output(tmp_path: Path) -> None:
    fixture = tmp_path / "rollout.jsonl"
    fixture.write_text(
        "\n".join(
            [
                '{"type":"session_meta","payload":{"id":"sess-1"}}',
                (
                    '{"timestamp":"2026-04-13T18:00:00Z","type":"event_msg","payload":'
                    '{"type":"exec_command_end","command":["/bin/bash","-lc","cat ~/.codex/AGENTS.md"],'
                    '"cwd":"/home/vostok","exit_code":0,'
                    '"stdout":"line ok\\n<claude-mem-context>secret</claude-mem-context>\\n'
                    '{\\"type\\":\\"response_item\\",\\"payload\\":{\\"type\\":\\"message\\",\\"role\\":\\"developer\\"}}\\n'
                    '{\\"type\\":\\"response_item\\",\\"payload\\":{\\"type\\":\\"reasoning\\",'
                    '\\"encrypted_content\\":\\"gAAAA...\\",\\"summary\\":[]}}\\nline final"}}'
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    chunks = extract_chunks(fixture, project_id="side_rag_real")

    assert len(chunks) == 1
    assert "line ok" in chunks[0].content
    assert "line final" in chunks[0].content
    assert "<claude-mem-context>" not in chunks[0].content
    assert "encrypted_content" not in chunks[0].content
    assert "response_item" not in chunks[0].content
    assert '"type":"reasoning"' not in chunks[0].content


def test_extract_chunks_ignores_response_item_root_type(tmp_path: Path) -> None:
    fixture = tmp_path / "response_item.jsonl"
    fixture.write_text(
        "\n".join(
            [
                '{"type":"session_meta","payload":{"id":"sess-1"}}',
                '{"type":"response_item","payload":{"type":"reasoning","encrypted_content":"gAAAA"}}',
                '{"timestamp":"2026-04-13T18:00:01Z","type":"event_msg","payload":{"type":"user_message","message":"hello"}}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    chunks = extract_chunks(fixture, project_id="side_rag_real")

    assert len(chunks) == 1
    assert chunks[0].source_event_type == "user_message"
    assert chunks[0].content == "hello"


def test_resolve_codex_session_file_finds_unique_match(tmp_path: Path) -> None:
    sessions_root = tmp_path / "sessions"
    target = sessions_root / "2026" / "04" / "13" / "rollout-2026-04-13T00-00-00-abc123.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{}", encoding="utf-8")

    resolved = resolve_codex_session_file(session_id="abc123", root=sessions_root)

    assert resolved == target
