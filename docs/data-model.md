# Data Model

Primary Phase 1 entity: `ChunkModel`

Required fields:

- `chunk_id`
- `project_id`
- `session_id`
- `content`
- `source_hash`
- `source_path`
- `source_event_type`
- `source_line_start`
- `source_line_end`
- `timestamp`
- `role`
- `phase`
- `prompt_number`
- `raw_chunk_id`
- `parser_version`
- `created_at`

Rules:

- `source_hash` is the idempotency key
- Phase 1 hash formula is `md5(f"{session_id}:{source_line_start}:{chunk_index}:{content}")`
- derived records must always point back to raw source
- code, stack traces, SQL, specs, and test output must not be summarized away in Phase 1
- `source_line_end` matches `source_line_start` in the current one-line JSONL parser and expands later if chunking spans ranges
