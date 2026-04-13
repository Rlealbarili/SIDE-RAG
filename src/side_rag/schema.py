from __future__ import annotations

from pydantic import BaseModel, Field


class ChunkModel(BaseModel):
    chunk_id: str
    project_id: str
    session_id: str
    content: str
    source_hash: str
    source_path: str
    source_event_type: str
    source_line_start: int
    source_line_end: int
    timestamp: str
    role: str = "unknown"
    phase: str = "raw"
    prompt_number: int | None = None
    raw_chunk_id: str | None = None
    parser_version: str
    created_at: str


class QueryEval(BaseModel):
    id: str
    query: str
    project: str | None = None
    expected_terms: list[str] = Field(default_factory=list)
    expected_files: list[str] = Field(default_factory=list)
    expected_chunk_ids: list[str] = Field(default_factory=list)
    required: bool = True
    source_hint: str | None = None
