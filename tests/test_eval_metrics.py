from side_rag.eval.metrics import compute_average_latency_ms, compute_hitrate_at_k, compute_mrr


def test_eval_metrics_are_deterministic() -> None:
    assert compute_hitrate_at_k([True, False, True]) == 2 / 3
    assert compute_mrr([1.0, 0.5, 0.0]) == 0.5
    assert compute_average_latency_ms([10.0, 20.0, 30.0]) == 20.0
