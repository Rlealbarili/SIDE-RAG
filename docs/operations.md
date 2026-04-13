# Operations

## Paths

- DB: `data/sidecar.db`
- eval results: `evals/results/`
- package source: `src/side_rag/`

## Useful Commands

Initialize/inspect DB:

```bash
python scripts/inspect_db.py
```

Dry-run ingest:

```bash
python scripts/ingest_codex_session.py --input tests/fixtures/codex_session_sample.jsonl --project sample_project --dry-run
```

Dry-run ingest with project inference from a real Codex rollout:

```bash
python scripts/ingest_codex_session.py --codex-session-id 019d7de2-8c24-7d02-bb46-73d8f5f76aef --dry-run
```

Batch dry-run over the newest sessions:

```bash
python scripts/ingest_codex_batch.py --limit 10 --dry-run
```

Smoke search:

```bash
python scripts/smoke_search.py --query "awaiting_captcha"
```

## Cleanup

```bash
rm -f data/sidecar.db
rm -rf data/chroma
```

## Phase 1 Validation

```bash
python -m pytest -q
python scripts/eval_retrieval.py --queries evals/eval_queries.json --top-k 5
python scripts/eval_retrieval.py --queries evals/eval_queries_side_rag_real.json --top-k 5
```
