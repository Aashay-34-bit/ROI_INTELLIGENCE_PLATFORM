from app.core.enums import TaskCategory
from app.core.schemas import MetricRecord
from app.metrics.aggregator import summarize


def test_roi_and_aggregation() -> None:
    result = summarize(
        [
            MetricRecord(
                request_id="a",
                task_category=TaskCategory.CLASSIFICATION,
                cost_usd=0.01,
                input_tokens=10,
                output_tokens=5,
            )
        ]
    )
    assert result["request_count"] == 1
    assert result["savings_pct"] > 0
