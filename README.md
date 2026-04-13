# SIDE-RAG

SIDE-RAG is an isolated memory and retrieval sidecar for engineering agents.
It starts with Codex JSONL transcripts, local docs, and project artifacts, then
builds a traceable retrieval layer with SQLite FTS5 first and optional semantic
retrieval later.

## Status

Current phase: Phase 1 implemented and in closeout.

This repository now has:

- isolated SQLite + FTS5 baseline
- idempotent ingest for fixture and real Codex transcripts
- real-session parser hardening for Codex rollout data
- deterministic eval on fixture and real-session queries
- project-id inference from transcript `cwd` metadata
- batch ingest CLI for multiple Codex sessions
- docs, ADRs, tests, and audit trail for Phase 1 closeout

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

Real Codex rollout by session id:

```bash
python scripts/ingest_codex_session.py \
  --codex-session-id 019d7de2-8c24-7d02-bb46-73d8f5f76aef \
  --dry-run
```

Latest Codex rollout under `~/.codex/sessions`:

```bash
python scripts/ingest_codex_session.py \
  --latest-codex-session \
  --project side_rag_latest \
  --dry-run
```

Use `--codex-session-id` for stable replay. `--latest-codex-session` is convenient, but it may point to an active transcript that is still growing.

Batch ingest newest Codex rollouts with per-session project inference:

```bash
python scripts/ingest_codex_batch.py --limit 10 --dry-run
```

Batch ingest only sessions rooted under a specific workspace:

```bash
python scripts/ingest_codex_batch.py \
  --cwd-prefix /home/vostok/SIDE-RAG \
  --limit 5 \
  --dry-run
```

Smoke search:

```bash
python scripts/smoke_search.py --query "CAPTCHA awaiting_captcha"
```

Eval:

```bash
python scripts/eval_retrieval.py --queries evals/eval_queries.json --top-k 5
```

Real-session benchmark:

```bash
python scripts/eval_retrieval.py --queries evals/eval_queries_side_rag_real.json --top-k 5
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

## Phase 1 Evidence

- closeout summary: `docs/phase-1-closeout.md`
- fixture benchmark results: `evals/results/phase1_fixture_eval.json`
- real-session benchmark results: `evals/results/phase1_real_eval.json`

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

1. Expand ingest from a single real session to multiple projects and sessions.
2. Improve signal-vs-noise handling in tool outputs based on benchmark data.
3. Define the Phase 2 semantic retrieval gate from measured gaps, not intuition.
4. Only after that, expose a read-only MCP surface.
