from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from side_rag.config import settings
from side_rag.schema import ChunkModel


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
    session_id = explicit_session_id or path.stem
    created_at = datetime.now(UTC).isoformat()
    chunk_limit = max_chunk_chars or settings.max_chunk_chars
    ignored_types = {item.lower() for item in (ignored_event_types or settings.ignored_event_types)}

    for line_no, event in iter_jsonl_events(path):
        source_event_type = str(event.get("type", "unknown"))
        if source_event_type.lower() in ignored_types:
            continue

        content = _extract_content(event).strip()
        if not content:
            continue

        role = str(event.get("role") or event.get("sender") or "unknown")
        timestamp = str(event.get("timestamp") or event.get("created_at") or created_at)

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
