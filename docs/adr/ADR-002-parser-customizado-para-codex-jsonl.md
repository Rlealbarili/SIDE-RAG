# ADR-002 - Parser Customizado Para Codex JSONL

## Status
Accepted

## Contexto

Codex transcripts are structured JSONL and do not require a heavy framework in the critical path.

## Decisao

Use a custom Python parser first.

## Consequencias

- lower complexity
- easier debugging
- easier idempotent ingest
