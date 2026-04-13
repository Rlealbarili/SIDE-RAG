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

Smoke search:

```bash
python scripts/smoke_search.py --query "awaiting_captcha"
```

## Cleanup

```bash
rm -f data/sidecar.db
rm -rf data/chroma
```
