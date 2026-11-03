import pytest
import respx

from app.core.enums import PrecisionTier, TaskCategory
from app.core.schemas import Node
from app.execution.task_executor import TaskExecutor
from app.providers.registry import ModelRegistry
from app.settings import get_settings


def _node(model_id: str) -> Node:
    return Node(
        node_id="precision-check",
        task="Classify this ticket",
        input="Classify this ticket",
        task_category=TaskCategory.CLASSIFICATION,
        model_id=model_id,
        precision=PrecisionTier.AWQ4,
    )


@pytest.mark.asyncio
async def test_mock_precision_is_unverified(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "mock")
    get_settings.cache_clear()
    registry = ModelRegistry()
    model = next(m for m in registry.candidates("mock") if m.tier == "small")
    result = await TaskExecutor(registry).execute(_node(model.id), {})
    assert result.precision_verified is False
    assert result.precision_requested == "awq4"
    assert "routing label" in result.precision_note
    get_settings.cache_clear()


@pytest.mark.asyncio
@pytest.mark.parametrize(("actual", "verified"), [("q4_K_M", False), ("awq4", True)])
async def test_ollama_precision_compares_observed_value(monkeypatch, actual, verified):
    monkeypatch.setenv("MODEL_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama.test")
    get_settings.cache_clear()
    registry = ModelRegistry()
    model = next(m for m in registry.candidates("ollama"))
    model.actual_precision = actual
    with respx.mock(base_url="http://ollama.test") as router:
        router.post("/api/generate").respond(200, json={"response": "neutral"})
        result = await TaskExecutor(registry).execute(_node(model.id), {})
    assert result.precision_verified is verified
    assert result.precision_requested == "awq4"
    assert result.observed_model_artifact == actual
    assert (result.precision_note is None) is verified
    get_settings.cache_clear()
