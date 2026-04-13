from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from side_rag.config import settings
from side_rag.schema import ChunkModel

CODEX_ROOT_TYPES = {"session_meta", "event_msg", "response_item", "turn_context", "compacted"}
IGNORED_ROOT_TYPES = {"session_meta", "response_item", "turn_context", "compacted"}
IGNORED_CODEX_EVENT_TYPES = {
    "context_compacted",
    "task_complete",
    "task_started",
    "token_count",
    "turn_aborted",
}
CLAUDE_MEM_BLOCK_RE = re.compile(r"<claude-mem-context>.*?</claude-mem-context>", re.DOTALL | re.IGNORECASE)
ENCRYPTED_CONTENT_RE = re.compile(r'"encrypted_content"\s*:')
REASONING_TYPE_RE = re.compile(r'"type"\s*:\s*"reasoning"')
RESPONSE_ITEM_TYPE_RE = re.compile(r'"type"\s*:\s*"response_item"')

logger = logging.getLogger(__name__)


def iter_jsonl_events(path: Path) -> list[tuple[int, dict[str, Any]]]:
    events: list[tuple[int, dict[str, Any]]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                events.append((line_no, json.loads(line)))
            except json.JSONDecodeError:
                events.append((line_no, {"type": "raw_text", "content": line}))
    return events


def list_codex_session_files(root: Path | None = None) -> list[Path]:
    sessions_root = root or settings.codex_sessions_dir
    if not sessions_root.exists():
        return []
    return sorted(sessions_root.rglob("rollout-*.jsonl"))


def resolve_codex_session_file(
    *,
    session_id: str | None = None,
    latest: bool = False,
    root: Path | None = None,
) -> Path:
    sessions_root = root or settings.codex_sessions_dir
    candidates = list_codex_session_files(sessions_root)
    if not candidates:
        raise FileNotFoundError(f"No Codex sessions found under {sessions_root}")

    if latest:
        return max(candidates, key=lambda path: path.stat().st_mtime)

    if session_id:
        matches = [path for path in candidates if session_id in path.name]
        if not matches:
            raise FileNotFoundError(f"No Codex session matched id {session_id!r} under {sessions_root}")
        if len(matches) > 1:
            raise FileExistsError(f"Multiple Codex sessions matched id {session_id!r}")
        return matches[0]

    raise ValueError("Provide session_id or latest=True to resolve a Codex session file")


def _extract_content(event: dict[str, Any]) -> str:
    if isinstance(event.get("content"), str):
        return event["content"]

    blocks = event.get("content")
    if isinstance(blocks, list):
        parts: list[str] = []
        for block in blocks:
            if isinstance(block, dict):
                text = block.get("text") or block.get("content")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts).strip()

    payload = event.get("payload")
    if isinstance(payload, dict):
        if isinstance(payload.get("content"), str):
            return payload["content"]
        if isinstance(payload.get("text"), str):
            return payload["text"]

    return json.dumps(event, ensure_ascii=False)


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float, bool)):
        return str(value)
    return json.dumps(value, ensure_ascii=False)


def _resolve_session_id(
    path: Path,
    events: list[tuple[int, dict[str, Any]]],
    explicit_session_id: str | None,
) -> str:
    if explicit_session_id:
        return explicit_session_id

    for _, event in events:
        if event.get("type") != "session_meta":
            continue
        payload = event.get("payload")
        if isinstance(payload, dict) and isinstance(payload.get("id"), str):
            return payload["id"]

    return path.stem


def _sanitize_exec_output(output: str) -> str:
    if not output:
        return ""

    cleaned = CLAUDE_MEM_BLOCK_RE.sub("", output)
    cleaned = cleaned.replace("<claude-mem-context>", "").replace("</claude-mem-context>", "")
    kept_lines: list[str] = []
    for line in cleaned.splitlines():
        if ENCRYPTED_CONTENT_RE.search(line) or REASONING_TYPE_RE.search(line) or RESPONSE_ITEM_TYPE_RE.search(line):
            continue
        kept_lines.append(line.rstrip())

    compacted = "\n".join(kept_lines).strip()
    return re.sub(r"\n{3,}", "\n\n", compacted)


def _build_exec_command_content(payload: dict[str, Any]) -> str:
    command = payload.get("command")
    command_text = " ".join(str(part) for part in command) if isinstance(command, list) else _stringify(command)
    parts: list[str] = []
    if command_text:
        parts.append(f"command: {command_text}")
    if payload.get("cwd"):
        parts.append(f"cwd: {payload['cwd']}")
    if payload.get("exit_code") is not None:
        parts.append(f"exit_code: {payload['exit_code']}")
    output = _sanitize_exec_output(
        _stringify(payload.get("aggregated_output") or payload.get("stdout") or payload.get("stderr"))
    )
    if output:
        parts.append(output)
    return "\n\n".join(part for part in parts if part.strip())


def _build_patch_apply_content(payload: dict[str, Any]) -> str:
    parts: list[str] = []
    changes = _stringify(payload.get("changes"))
    if changes:
        parts.append(changes)
    stdout = _stringify(payload.get("stdout"))
    if stdout:
        parts.append(stdout)
    stderr = _stringify(payload.get("stderr"))
    if stderr:
        parts.append(stderr)
    return "\n\n".join(part for part in parts if part.strip())


def _build_mcp_tool_content(payload: dict[str, Any]) -> str:
    parts: list[str] = []
    invocation = _stringify(payload.get("invocation"))
    if invocation:
        parts.append(f"invocation: {invocation}")
    result = _stringify(payload.get("result"))
    if result:
        parts.append(f"result: {result}")
    return "\n\n".join(part for part in parts if part.strip())


def _build_web_search_content(payload: dict[str, Any]) -> str:
    parts: list[str] = []
    action = _stringify(payload.get("action"))
    if action:
        parts.append(f"action: {action}")
    query = _stringify(payload.get("query"))
    if query:
        parts.append(f"query: {query}")
    return "\n\n".join(part for part in parts if part.strip())


def _normalize_codex_event(event: dict[str, Any]) -> tuple[str, str, str, str] | None:
    root_type = str(event.get("type", "unknown"))
    if root_type in IGNORED_ROOT_TYPES:
        return None

    payload = event.get("payload")
    timestamp = str(event.get("timestamp") or datetime.now(UTC).isoformat())
    if root_type == "event_msg" and isinstance(payload, dict):
        event_type = str(payload.get("type", "unknown"))
        if event_type in IGNORED_CODEX_EVENT_TYPES or event_type in settings.ignored_event_types:
            return None

        if event_type == "user_message":
            return event_type, "user", timestamp, _stringify(payload.get("message"))
        if event_type == "agent_message":
            return event_type, "assistant", timestamp, _stringify(payload.get("message"))
        if event_type == "exec_command_end":
            return event_type, "tool", timestamp, _build_exec_command_content(payload)
        if event_type == "patch_apply_end":
            return event_type, "tool", timestamp, _build_patch_apply_content(payload)
        if event_type == "mcp_tool_call_end":
            return event_type, "tool", timestamp, _build_mcp_tool_content(payload)
        if event_type == "web_search_end":
            return event_type, "tool", timestamp, _build_web_search_content(payload)
        logger.debug("Ignoring unsupported Codex event_msg payload type: %s", event_type)
        return None

    if root_type in CODEX_ROOT_TYPES:
        logger.debug("Ignoring unsupported Codex root type: %s", root_type)
        return None

    content = _extract_content(event).strip()
    if not content:
        return None

    return (
        root_type,
        str(event.get("role") or event.get("sender") or "unknown"),
        str(event.get("timestamp") or event.get("created_at") or datetime.now(UTC).isoformat()),
        content,
    )


def _split_content(content: str, max_chunk_chars: int) -> list[str]:
    if max_chunk_chars <= 0 or len(content) <= max_chunk_chars:
        return [content]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for word in content.split():
        if len(word) > max_chunk_chars:
            if current:
                chunks.append(" ".join(current))
                current = []
                current_len = 0
            for start in range(0, len(word), max_chunk_chars):
                chunks.append(word[start : start + max_chunk_chars])
            continue

        projected = current_len + len(word) + (1 if current else 0)
        if current and projected > max_chunk_chars:
            chunks.append(" ".join(current))
            current = [word]
            current_len = len(word)
            continue

        current.append(word)
        current_len = projected

    if current:
        chunks.append(" ".join(current))

    return chunks or [content[:max_chunk_chars]]


def _build_source_hash(session_id: str, line_no: int, chunk_index: int, content: str) -> str:
    seed = f"{session_id}:{line_no}:{chunk_index}:{content}"
    return hashlib.md5(seed.encode("utf-8")).hexdigest()


def extract_chunks(
    path: Path,
    project_id: str,
    explicit_session_id: str | None = None,
    *,
    max_chunk_chars: int | None = None,
    ignored_event_types: set[str] | frozenset[str] | None = None,
) -> list[ChunkModel]:
    chunks: list[ChunkModel] = []
    events = iter_jsonl_events(path)
    session_id = _resolve_session_id(path, events, explicit_session_id)
    created_at = datetime.now(UTC).isoformat()
    chunk_limit = max_chunk_chars or settings.max_chunk_chars
    ignored_types = {item.lower() for item in (ignored_event_types or settings.ignored_event_types)}

    for line_no, event in events:
        normalized = _normalize_codex_event(event)
        if not normalized:
            continue

        source_event_type, role, timestamp, content = normalized
        if source_event_type.lower() in ignored_types:
            continue
        if not content:
            continue

        for chunk_index, chunk_content in enumerate(_split_content(content, chunk_limit), start=1):
            chunks.append(
                ChunkModel(
                    chunk_id=str(uuid4()),
                    project_id=project_id,
                    session_id=session_id,
                    content=chunk_content,
                    source_hash=_build_source_hash(session_id, line_no, chunk_index, chunk_content),
                    source_path=str(path),
                    source_event_type=source_event_type,
                    source_line_start=line_no,
                    source_line_end=line_no,
                    timestamp=timestamp,
                    role=role,
                    phase="raw",
                    prompt_number=None,
                    raw_chunk_id=None,
                    parser_version=settings.parser_version,
                    created_at=created_at,
                )
            )

    return chunks
