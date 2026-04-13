# ADR-001 - Sidecar Isolated From claude-mem

## Status
Accepted

## Contexto

`claude-mem` is already operational and should not be destabilized by SIDE-RAG.

## Decisao

SIDE-RAG will use its own storage and indexes.

## Consequencias

- simpler rollback
- independent schema evolution
- explicit integrations only
