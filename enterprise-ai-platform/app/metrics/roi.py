def savings_percent(actual_cost: float, baseline_cost: float) -> float:
    return (baseline_cost - actual_cost) / baseline_cost * 100 if baseline_cost else 0.0
