import httpx
import respx
from fastapi.testclient import TestClient

from app.api.deps import get_registry, get_router
from app.main import app
from app.settings import get_settings


def _reset():
    get_settings.cache_clear()
    get_registry.cache_clear()
    get_router.cache_clear()


def test_strict_privacy_classification_goes_edge(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama.test")
    _reset()
    with respx.mock(base_url="http://ollama.test") as router:
        router.get("/api/tags").respond(200, json={"models": [{"name": "qwen3.5:4b"}]})
        router.post("/api/generate").respond(200, json={"response": "neutral"})
        with TestClient(app) as client:
            response = client.post(
                "/v1/request",
                headers={"X-API-Key": "demo-key"},
                json={
                    "input": "Classify this support ticket",
                    "task_category": "classification",
                    "privacy": "strict",
                },
            )
    assert response.status_code == 200
    node = response.json()["trace"]["nodes"][0]
    assert node["provider"] == "ollama"
    assert node["is_edge"] is True
    assert node["edge_rationale"]
    _reset()


def test_strict_privacy_reasoning_records_capability_escalation(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "mock")
    _reset()
    with TestClient(app) as client:
        response = client.post(
            "/v1/request",
            headers={"X-API-Key": "demo-key"},
            json={
                "input": "Reason about this ticket",
                "task_category": "reasoning",
                "privacy": "strict",
            },
        )
    assert response.status_code == 200
    node = response.json()["trace"]["nodes"][0]
    assert node["is_edge"] is False
    assert node["escalation_reason"] == "edge_capability_exceeded"
    _reset()


def test_edge_unavailable_returns_503(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama.test")
    _reset()
    with respx.mock(base_url="http://ollama.test") as router:
        router.get("/api/tags").mock(side_effect=httpx.ConnectError("offline"))
        with TestClient(app) as client:
            response = client.post(
                "/v1/request",
                headers={"X-API-Key": "demo-key"},
                json={
                    "input": "Classify this ticket",
                    "task_category": "classification",
                    "privacy": "strict",
                },
            )
    assert response.status_code == 503
    assert response.json()["error"] == "edge_unavailable"
    _reset()
