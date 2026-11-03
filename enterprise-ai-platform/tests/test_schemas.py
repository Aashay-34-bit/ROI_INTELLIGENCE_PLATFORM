import pytest
from pydantic import ValidationError

from app.core.enums import PrecisionTier, TaskCategory
from app.core.schemas import ModelSpec, Node, Plan, Request


def test_request_defaults_and_serialization() -> None:
    request = Request(input="hello", task_category=TaskCategory.CLASSIFICATION)
    assert request.model_dump(mode="json")["task_category"] == "classification"


def test_plan_and_model_schema() -> None:
    node = Node(node_id="a", task="classify", task_category=TaskCategory.CLASSIFICATION)
    assert Plan(nodes=[node]).nodes[0].status == "pending"
    spec = ModelSpec(id="m", tier="small", precisions=[PrecisionTier.AWQ4])
    assert spec.precisions == [PrecisionTier.AWQ4]


def test_request_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        Request(input="x", unexpected=True)
