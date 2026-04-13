# PHASE_1_PLAN

## Goal

Build the offline ETL and deterministic evaluation baseline for SIDE-RAG.

## Scope

- parse Codex JSONL transcripts with a custom Python parser
- normalize into a canonical chunk model
- persist to isolated SQLite with FTS5
- support idempotent re-ingest via `source_hash`
- expose a simple lexical retrieval path
- measure retrieval quality with deterministic metrics

## Deliverables

- `src/side_rag/schema.py`
- `src/side_rag/db.py`
- `src/side_rag/parsers/codex_parser.py`
- `src/side_rag/indexer/processor.py`
- `src/side_rag/retrieval/fts.py`
- `scripts/ingest_codex_session.py`
- `scripts/eval_retrieval.py`
- `evals/eval_queries.json`
- parser, schema, idempotency, and FTS tests

## Out Of Scope

- GraphRAG
- Mem0
- write-back to `claude-mem`
- production MCP write flows
- mandatory embeddings or reranking

## Acceptance Criteria

- ingest runs without touching `claude-mem`
- running ingest twice does not duplicate chunks
- search returns chunk content plus source metadata
- required eval queries achieve useful baseline recall
- rollback is limited to SIDE-RAG artifacts

## Execution Order

1. schema and SQLite foundation
2. parser against fixture transcripts
3. ingest pipeline and idempotency
4. FTS retrieval
5. smoke CLI
6. evaluation CLI
7. docs and ADR sync
