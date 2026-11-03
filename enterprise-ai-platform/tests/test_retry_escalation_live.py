import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_registry, get_router
from app.core.enums import PrecisionTier, TaskCategory
from app.core.schemas import Node
from app.execution.task_executor import TaskExecutor
from app.main import app
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


def test_always_fail_hits_budget_then_returns_422(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "mock")
    monkeypatch.setenv("MOCK_MODE", "always_fail")
    get_settings.cache_clear()
    get_registry.cache_clear()
    get_router.cache_clear()
    with TestClient(app) as client:
        response = client.post(
            "/v1/request",
            headers={"X-API-Key": "demo-key"},
            json={"input": "Classify this", "task_category": "classification"},
        )
    assert response.status_code == 422
    assert response.json()["error"] == "task_execution_failed"
    get_settings.cache_clear()
    get_registry.cache_clear()
    get_router.cache_clear()
