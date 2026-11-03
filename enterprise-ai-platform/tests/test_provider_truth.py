from datetime import UTC, datetime

from app.core.enums import TaskCategory
from app.core.schemas import MetricRecord
from app.metrics.aggregator import provider_truth


def _record(request_id: str, provider: str, verified: bool = False, edge: bool = False):
    return MetricRecord(
        request_id=request_id,
        task_category=TaskCategory.CLASSIFICATION,
        nodes=[
            {
                "provider": provider,
                "model_id": "test-model",
                "is_edge": edge,
                "precision_verified": verified,
                "precision_requested": "awq4",
                "observed_model_artifact": "awq4" if verified else None,
            }
        ],
        created_at=datetime.now(UTC),
    )


def test_provider_truth_distinguishes_mock_and_real_calls():
    mock = provider_truth([_record("mock", "mock")], [], window=100)
    assert mock["has_real_calls"] is False
    assert mock["by_provider"]["mock"] == 1
    assert mock["by_precision_verified"]["false"] == 1

    real = provider_truth([_record("ollama", "ollama", verified=True, edge=True)], [], window=100)
    assert real["has_real_calls"] is True
    assert real["by_provider"]["edge"] == 1
    assert real["by_precision_verified"]["true"] == 1


def test_provider_truth_includes_recent_503_errors():
    errors = [{"timestamp": "now", "status_code": 503, "error": "ollama_unreachable"}]
    result = provider_truth([], errors)
    assert result["recent_errors"] == errors
