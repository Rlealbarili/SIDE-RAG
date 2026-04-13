# SIDE-RAG

SIDE-RAG is an isolated memory and retrieval sidecar for engineering agents.
It starts with Codex JSONL transcripts, local docs, and project artifacts, then
builds a traceable retrieval layer with SQLite FTS5 first and optional semantic
retrieval later.

## Status

Current phase: foundation scaffold created.

This repository now has:

- project structure for Phase 1
- Python package skeleton under `src/side_rag/`
- CLI entry scripts for ingest, eval, inspect, and smoke search
- docs and ADR placeholders aligned with the planning documents
- tests and fixtures to drive the first implementation slice

## Principles

- isolated from `claude-mem`
- raw source preserved, derived index rebuildable
- every retrieval result must point to a source
- benchmark before optimization
- rollback must be simple

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the baseline test gate before changing retrieval behavior:

```bash
python -m pytest -q
```

Initialize the sidecar DB:

```bash
python scripts/inspect_db.py
```

Dry-run transcript parsing:

```bash
python scripts/ingest_codex_session.py \
  --input tests/fixtures/codex_session_sample.jsonl \
  --project sample_project \
  --dry-run
```

Real ingest:

```bash
python scripts/ingest_codex_session.py \
  --input tests/fixtures/codex_session_sample.jsonl \
  --project sample_project
```

Smoke search:

```bash
python scripts/smoke_search.py --query "CAPTCHA awaiting_captcha"
```

Eval:

```bash
python scripts/eval_retrieval.py --queries evals/eval_queries.json --top-k 5
```

The initial eval measures:

- HitRate@K
- MRR
- average latency in milliseconds
- expected term, file, and chunk-id coverage in top-K

## Rollback

The initial rollback remains simple:

```bash
rm -f data/sidecar.db
rm -rf data/chroma
```

This does not touch `claude-mem`.

## Repository Layout

```text
SIDE-RAG/
├── docs/
├── data/
├── evals/
├── mcp/
├── scripts/
├── src/side_rag/
└── tests/
```

## Next Implementation Slice

1. Harden the Codex JSONL parser against real transcripts.
2. Implement idempotent ingest into SQLite.
3. Validate FTS5 retrieval against required eval queries.
4. Only then decide whether vector search is worth enabling.
