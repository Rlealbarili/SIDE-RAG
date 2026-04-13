#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from side_rag.config import settings
from side_rag.db import connect_db, initialize_db
from side_rag.eval.metrics import compute_average_latency_ms, compute_hitrate_at_k, compute_mrr
from side_rag.retrieval.fts import search_fts
from side_rag.schema import QueryEval


def _matches_expected_term(row: dict, expected_terms: list[str]) -> bool:
    if not expected_terms:
        return False
    content = (row.get("content") or "").lower()
    return any(term.lower() in content for term in expected_terms)


def _matches_expected_file(row: dict, expected_files: list[str]) -> bool:
    if not expected_files:
        return False
    haystack = "\n".join(
        [
            row.get("content") or "",
            row.get("source_path") or "",
        ]
    ).lower()
    return any(path.lower() in haystack for path in expected_files)


def _matches_expected_chunk(row: dict, expected_chunk_ids: list[str]) -> bool:
    if not expected_chunk_ids:
        return False
    return row.get("chunk_id") in expected_chunk_ids


def _query_passed(item: QueryEval, hits: list[dict]) -> tuple[bool, float, dict[str, object]]:
    term_hit = not item.expected_terms
    file_hit = not item.expected_files
    chunk_hit = not item.expected_chunk_ids
    reciprocal_rank = 0.0

    for idx, row in enumerate(hits, start=1):
        row_term_hit = _matches_expected_term(row, item.expected_terms)
        row_file_hit = _matches_expected_file(row, item.expected_files)
        row_chunk_hit = _matches_expected_chunk(row, item.expected_chunk_ids)

        term_hit = term_hit or row_term_hit
        file_hit = file_hit or row_file_hit
        chunk_hit = chunk_hit or row_chunk_hit

        if reciprocal_rank == 0.0 and (row_term_hit or row_file_hit or row_chunk_hit):
            reciprocal_rank = 1.0 / idx

    matched = term_hit and file_hit and chunk_hit
    return matched, reciprocal_rank, {
        "matched_terms": term_hit,
        "matched_files": file_hit,
        "matched_chunk_ids": chunk_hit,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic retrieval evals.")
    parser.add_argument("--queries", required=True, help="Path to eval_queries.json.")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    queries_path = Path(args.queries).expanduser().resolve()
    queries = [QueryEval.model_validate(item) for item in json.loads(queries_path.read_text())]

    conn = connect_db(settings.db_path)
    initialize_db(conn)

    scores = []
    for item in queries:
        started_at = time.perf_counter()
        hits = search_fts(conn, item.query, limit=args.top_k, project_id=item.project)
        latency_ms = (time.perf_counter() - started_at) * 1000
        matched, reciprocal_rank, detail = _query_passed(item, hits)
        scores.append(
            {
                "id": item.id,
                "required": item.required,
                "project": item.project,
                "hit": matched,
                "rr": reciprocal_rank,
                "latency_ms": round(latency_ms, 3),
                **detail,
            }
        )

    print(
        json.dumps(
            {
                "queries": len(scores),
                "hit_rate_at_k": compute_hitrate_at_k([s["hit"] for s in scores]),
                "mrr": compute_mrr([s["rr"] for s in scores]),
                "latency_ms_avg": compute_average_latency_ms([s["latency_ms"] for s in scores]),
                "details": scores,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
