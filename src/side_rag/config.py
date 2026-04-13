from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    project_root: Path
    data_dir: Path
    db_path: Path
    codex_sessions_dir: Path
    parser_version: str
    max_chunk_chars: int
    ignored_event_types: frozenset[str]


def _path_from_env(name: str, default: Path) -> Path:
    raw = os.environ.get(name)
    if not raw:
        return default
    return Path(raw).expanduser().resolve()


def _int_from_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if not raw:
        return default
    return int(raw)


def _csv_set_from_env(name: str, default: str) -> frozenset[str]:
    raw = os.environ.get(name, default)
    return frozenset(part.strip().lower() for part in raw.split(",") if part.strip())


PROJECT_ROOT = _path_from_env(
    "SIDE_RAG_PROJECT_ROOT",
    Path(__file__).resolve().parents[2],
)
DATA_DIR = _path_from_env("SIDE_RAG_DATA_DIR", PROJECT_ROOT / "data")

settings = Settings(
    project_root=PROJECT_ROOT,
    data_dir=DATA_DIR,
    db_path=_path_from_env("SIDE_RAG_DB_PATH", DATA_DIR / "sidecar.db"),
    codex_sessions_dir=_path_from_env("SIDE_RAG_CODEX_SESSIONS_DIR", Path.home() / ".codex" / "sessions"),
    parser_version=os.environ.get("SIDE_RAG_PARSER_VERSION", "0.1.0"),
    max_chunk_chars=_int_from_env("SIDE_RAG_MAX_CHUNK_CHARS", 8000),
    ignored_event_types=_csv_set_from_env(
        "SIDE_RAG_IGNORED_EVENT_TYPES",
        "token_count,summary_count",
    ),
)
