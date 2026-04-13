from __future__ import annotations


def reciprocal_rank_fusion(result_sets: list[list[dict]], k: int = 60) -> list[dict]:
    scores: dict[str, float] = {}
    by_id: dict[str, dict] = {}
    for result_set in result_sets:
        for rank, row in enumerate(result_set, start=1):
            chunk_id = row["chunk_id"]
            by_id[chunk_id] = row
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
    return [by_id[chunk_id] for chunk_id, _ in sorted(scores.items(), key=lambda item: item[1], reverse=True)]
