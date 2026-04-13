# Phase 1 Closeout

## Scope Achieved

Phase 1 delivered the offline ETL and deterministic retrieval baseline for
SIDE-RAG:

- custom parser for Codex JSONL transcripts
- canonical chunk schema with source metadata
- isolated SQLite database with FTS5
- idempotent ingest driven by `source_hash`
- deterministic eval for fixture and real-session queries
- rollback limited to SIDE-RAG artifacts

## Validation Commands

```bash
python -m pytest -q
python scripts/eval_retrieval.py --queries evals/eval_queries.json --top-k 5
python scripts/eval_retrieval.py --queries evals/eval_queries_side_rag_real.json --top-k 5
python scripts/ingest_codex_batch.py --cwd-prefix /home/vostok/SIDE-RAG --limit 10 --dry-run
```

## Acceptance Snapshot

- `pytest`: 16 tests passing
- fixture benchmark: `HitRate@5 = 1.0`, `MRR = 1.0`, `latency_ms_avg = 0.9155`
- real benchmark: `HitRate@5 = 1.0`, `MRR = 1.0`, `latency_ms_avg = 2.234`
- indexed rows after closeout rebuild: `1048`
  - `sample_project`: `3`
  - `side_rag`: `1045`
- real-session parser hardened against raw `response_item`, `reasoning`, and
  `claude-mem-context` payload leakage inside `exec_command_end`
- `project_id` can be inferred from transcript `cwd` metadata when present
- batch ingest path exists for multi-session validation before MCP
- dry-run over the newest SIDE-RAG sessions found `5` inferable sessions with
  stable `project_id = side_rag`

## Frozen Artifacts

- `evals/results/phase1_fixture_eval.json`
- `evals/results/phase1_real_eval.json`
- `evals/results/phase1_batch_dry_run.json`
- `evals/results/phase1_db_summary.json`

## Residual Risks

- `project_id` inference depends on `cwd` metadata being meaningful
- one-session real benchmark is enough to close Phase 1, but not enough to
  justify semantic retrieval or MCP behavior decisions alone
- tool output still needs signal-vs-noise tuning as more projects are ingested

## Out of Scope for Phase 1

- semantic retrieval as the default path
- reranker in the critical path
- MCP read-only server behavior
- any write-back to `claude-mem`
