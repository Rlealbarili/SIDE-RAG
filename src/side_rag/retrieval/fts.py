from __future__ import annotations

import re
import sqlite3

STOPWORDS = {
    "a",
    "as",
    "como",
    "com",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "foi",
    "na",
    "nas",
    "no",
    "nos",
    "o",
    "os",
    "para",
    "por",
    "qual",
    "que",
    "sobre",
    "um",
    "uma",
}
TOKEN_RE = re.compile(r"[\w_]+", re.UNICODE)


def sanitize_fts_query(query: str) -> str:
    tokens: list[str] = []
    for token in TOKEN_RE.findall(query):
        normalized = token.strip()
        lowered = normalized.lower()
        if len(lowered) < 3 and "_" not in lowered and not lowered.isdigit():
            continue
        if lowered in STOPWORDS:
            continue
        tokens.append(normalized.replace('"', ""))

    if not tokens:
        fallback = query.strip().replace('"', "")
        return f'"{fallback}"' if fallback else '""'

    unique_tokens = list(dict.fromkeys(tokens))
    return " OR ".join(f'"{token}"' for token in unique_tokens)


def search_fts(
    conn: sqlite3.Connection,
    query: str,
    limit: int = 5,
    project_id: str | None = None,
) -> list[dict]:
    sanitized_query = sanitize_fts_query(query)
    if sanitized_query == '""':
        return []

    sql = """
        SELECT c.*, bm25(chunks_fts) AS score
        FROM chunks_fts f
        JOIN chunks c ON c.chunk_id = f.chunk_id
        WHERE chunks_fts MATCH ?
    """
    params: list[object] = [sanitized_query]
    if project_id:
        sql += " AND c.project_id = ?"
        params.append(project_id)
    sql += " ORDER BY score LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]
