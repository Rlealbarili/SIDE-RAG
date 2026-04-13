from __future__ import annotations


def compute_hitrate_at_k(hits: list[bool]) -> float:
    if not hits:
        return 0.0
    return sum(1 for hit in hits if hit) / len(hits)


def compute_mrr(reciprocal_ranks: list[float]) -> float:
    if not reciprocal_ranks:
        return 0.0
    return sum(reciprocal_ranks) / len(reciprocal_ranks)


def compute_average_latency_ms(latencies_ms: list[float]) -> float:
    if not latencies_ms:
        return 0.0
    return sum(latencies_ms) / len(latencies_ms)
