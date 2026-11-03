from collections import defaultdict

from app.core.schemas import MetricRecord


def summarize(records: list[MetricRecord]) -> dict[str, object]:
    categories: dict[str, int] = defaultdict(int)
    tokens_by_tier: dict[str, int] = defaultdict(int)
    tokens_by_precision: dict[str, int] = defaultdict(int)
    cost_by_model: dict[str, float] = defaultdict(float)
    edge_nodes = cloud_nodes = 0
    cost = sum(r.cost_usd for r in records)
    successful = sum(r.successful for r in records)
    for r in records:
        categories[r.task_category.value] += 1
        for node in r.nodes:
            tokens = int(node.get("input_tokens", 0)) + int(node.get("output_tokens", 0))
            tokens_by_tier[str(node.get("tier", "unknown"))] += tokens
            tokens_by_precision[str(node.get("precision", "unknown"))] += tokens
            cost_by_model[str(node.get("model_id", "unknown"))] += float(node.get("cost_usd", 0))
            if node.get("is_edge"):
                edge_nodes += 1
            else:
                cloud_nodes += 1
    baseline = sum(max(1, r.input_tokens + r.output_tokens) * (2.5 + 10) / 1000 for r in records)
    return {
        "request_count": len(records),
        "cost_usd": cost,
        "successful": successful,
        "success_rate": successful / max(1, len(records)),
        "baseline_cost_usd": baseline,
        "savings_pct": (baseline - cost) / baseline * 100 if baseline else 0,
        "cost_per_successful_task": cost / max(1, successful),
        "retry_rate": sum(r.retry_count for r in records) / max(1, len(records)),
        "escalation_rate": sum(r.escalation_count for r in records) / max(1, len(records)),
        "parallel_efficiency": sum(r.parallel_efficiency for r in records) / max(1, len(records)),
        "critical_path_latency_ms": sum(r.critical_path_latency_ms for r in records)
        / max(1, len(records)),
        "total_work_latency_ms": sum(r.latency_ms for r in records),
        "token_consumption_by_tier": dict(tokens_by_tier),
        "token_consumption_by_precision": dict(tokens_by_precision),
        "cost_by_model": dict(cost_by_model),
        "jev_decision_coverage": sum(r.jev_decisions_covered for r in records)
        / max(1, sum(r.jev_decision_count for r in records)),
        "edge_offload_rate": edge_nodes / max(1, edge_nodes + cloud_nodes),
        "by_category": dict(categories),
    }
