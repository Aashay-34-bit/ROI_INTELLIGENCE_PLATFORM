import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from app.api.deps import get_registry, get_router
from app.core.errors import ProviderNotAvailable
from app.main import app
from app.providers.mock_adapter import MockAdapter
from app.providers.registry import ModelRegistry
from app.settings import get_settings


@pytest.fixture(autouse=True)
def clear_provider_caches():
    get_settings.cache_clear()
    get_registry.cache_clear()
    get_router.cache_clear()
    yield
    get_settings.cache_clear()
    get_registry.cache_clear()
    get_router.cache_clear()


def test_adapter_mock_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MODEL_PROVIDER", raising=False)
    get_settings.cache_clear()
    adapter = ModelRegistry().adapter("mock-small-fp8")
    assert isinstance(adapter, MockAdapter)


def test_adapter_ollama_requires_ollama_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MODEL_PROVIDER", "ollama")
    get_settings.cache_clear()
    with pytest.raises(ProviderNotAvailable):
        ModelRegistry().adapter("mock-small-fp8")


def test_candidates_filter(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MODEL_PROVIDER", "ollama")
    get_settings.cache_clear()
    candidates = ModelRegistry().candidates("ollama")
    assert [model.id for model in candidates] == ["qwen3.5:4b"]


def test_ollama_unreachable_returns_503(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MODEL_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama.test")
    monkeypatch.setenv("MOCK_MIN_LATENCY_MS", "0")
    monkeypatch.setenv("MOCK_MAX_LATENCY_MS", "0")
    get_settings.cache_clear()
    get_registry.cache_clear()
    get_router.cache_clear()
    with respx.mock(assert_all_called=True) as mock_router:
        mock_router.get("http://ollama.test/api/tags").mock(
            side_effect=httpx.ConnectError("Ollama is offline")
        )
        with TestClient(app) as client:
            response = client.post(
                "/v1/request",
                headers={"X-API-Key": "demo-key"},
                json={
                    "input": "Classify this neutral customer message",
                    "task_category": "classification",
                },
            )
    assert response.status_code == 503
    assert response.json()["error"] == "ollama_unreachable"
