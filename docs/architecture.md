# Architecture

Phase 1 architecture:

```text
Codex JSONL / docs / specs
        |
        v
custom parser
        |
        v
canonical chunks
        |
        +--> SQLite sidecar.db + FTS5
        +--> optional vector store later
        |
        v
retrieval + deterministic eval
```

Key decisions:

- parser first, framework later
- lexical retrieval first, semantic retrieval optional
- raw source preserved through metadata
- no direct coupling to `claude-mem`
