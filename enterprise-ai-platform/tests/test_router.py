from app.core.enums import TaskCategory
from app.core.schemas import Request
from app.providers.registry import ModelRegistry
from app.routing.precision_policy import PrecisionPolicy
from app.routing.router import Router


def test_classification_routes_to_small_model() -> None:
    request = Request(input="classify this", task_category=TaskCategory.CLASSIFICATION)
    decision = Router(ModelRegistry(), PrecisionPolicy()).route(request)
    assert "advanced" not in decision.model_id


def test_precision_policy_and_reasoning_quality() -> None:
    decision = Router(ModelRegistry(), PrecisionPolicy()).route(
        Request(input="compare these options", task_category=TaskCategory.REASONING)
    )
    assert decision.model_id == "mock-medium-fp8"
