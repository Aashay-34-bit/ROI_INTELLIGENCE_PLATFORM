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


def provider_truth(
    records: list[MetricRecord], recent_errors: list[dict[str, object]], window: int = 100
) -> dict[str, object]:
    recent = records[-window:]
    providers = {key: 0 for key in ("mock", "ollama", "openai", "anthropic", "edge")}
    precision = {"true": 0, "false": 0}
    node_rows: list[dict[str, object]] = []
    real = False
    for record in recent:
        for node in record.nodes:
            provider = str(node.get("provider", "unknown")).lower()
            real = real or provider != "mock"
            bucket = "edge" if node.get("is_edge") else provider
            providers[bucket] = providers.get(bucket, 0) + 1
            verified = bool(node.get("precision_verified", False))
            precision[str(verified).lower()] += 1
            node_rows.append(
                {
                    "request_id": record.request_id,
                    "created_at": record.created_at.isoformat(),
                    "provider": provider,
                    "model_id": node.get("model_id"),
                    "precision_requested": node.get("precision_requested"),
                    "observed_model_artifact": node.get("observed_model_artifact"),
                    "precision_verified": verified,
                    "precision_note": node.get("precision_note"),
                }
            )
    return {
        "window": len(recent),
        "by_provider": providers,
        "by_precision_verified": precision,
        "recent_errors": recent_errors[:5],
        "has_real_calls": real,
        "recent_nodes": node_rows[-100:],
    }
