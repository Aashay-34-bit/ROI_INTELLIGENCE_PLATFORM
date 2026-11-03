import pytest

from app.core.enums import PrecisionTier, TaskCategory
from app.core.schemas import Node
from app.execution.task_executor import TaskExecutor
from app.providers.mock_adapter import reset_flaky_state
from app.providers.registry import ModelRegistry
from app.settings import get_settings


@pytest.mark.asyncio
async def test_flaky_first_triggers_retry_then_escalation(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "mock")
    monkeypatch.setenv("MOCK_MODE", "flaky_first")
    monkeypatch.setenv("MOCK_FAIL_FIRST_MODEL", "mock-small-fp8")
    monkeypatch.setenv("MAX_RETRIES_PER_NODE", "0")
    monkeypatch.setenv("MAX_RETRIES_PER_REQUEST", "0")
    get_settings.cache_clear()
    reset_flaky_state()
    registry = ModelRegistry()
    small = next(m for m in registry.candidates("mock") if m.tier == "small")
    node = Node(
        node_id="demo",
        task="Classify this positive message",
        input="Classify this positive message",
        task_category=TaskCategory.CLASSIFICATION,
        model_id=small.id,
        precision=PrecisionTier.AWQ4,
    )
    result = await TaskExecutor(registry).execute(node, {})
    assert result.attempts >= 2
    assert result.escalated is True
    assert result.escalated_from == small.id
    assert result.escalation_count == 1
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_always_fail_hits_budget_then_escalates(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "mock")
    monkeypatch.setenv("MOCK_MODE", "always_fail")
    get_settings.cache_clear()
    registry = ModelRegistry()
    small = next(m for m in registry.candidates("mock") if m.tier == "small")
    node = Node(
        node_id="demo",
        task="Classify this",
        input="Classify this",
        task_category=TaskCategory.CLASSIFICATION,
        model_id=small.id,
    )
    with pytest.raises(RuntimeError, match="simulated mock failure"):
        await TaskExecutor(registry).execute(node, {})
    get_settings.cache_clear()
