# Eval Data

`eval_queries.json` is the deterministic fixture benchmark for Phase 1.

`eval_queries_side_rag_real.json` is the first grounded benchmark over a real
Codex session indexed into `side_rag_real`.

Each entry may use:

- `expected_terms`
- `expected_files`
- `expected_chunk_ids`

Committed benchmark artifacts for Phase 1 closeout live under `evals/results/`.
