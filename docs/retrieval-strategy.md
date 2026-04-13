# Retrieval Strategy

Phase 1 retrieval:

- SQLite FTS5 for lexical search
- natural-language queries sanitized before FTS5 `MATCH`
- metadata-aware indexing for `project_id`, `session_id`, source path, event type, and role
- no mandatory vector search
- no mandatory reranker

Future path:

- optional vector retrieval
- optional reciprocal rank fusion
- optional reranker only after benchmark proves value
