from fastapi.testclient import TestClient

from app.main import app
from app.routing.jev_mock import JevMockBackend


def _request(text: str, category: str = "classification"):
    return TestClient(app).post(
        "/v1/request",
        headers={"X-API-Key": "demo-key"},
        json={"input": text, "task_category": category},
    )


def test_jev_decision_gates_billing_routing():
    response = _request("I was charged twice for my subscription. Please refund.")
    assert response.status_code == 200
    trace = response.json()["trace"]
    assert trace["jev_decisions"]["refund_request"]["choice"] == "Yes"
    assert trace["routing_path"] == "jev_map:refund_request=Yes -> rule:billing_handler"
    assert trace["nodes"] == []
    assert response.json()["result"]["category"] == "Billing"


def test_jev_no_match_falls_through_to_strategy():
    response = _request("What are your business hours?")
    trace = response.json()["trace"]
    assert response.status_code == 200
    assert trace["routing_path"] == "jev_no_match -> strategy"
    assert len(trace["nodes"]) == 1


def test_jev_failure_falls_back(monkeypatch):
    async def fail(self, input, questions):
        raise RuntimeError("Jev offline")

    monkeypatch.setattr(JevMockBackend, "decide", fail)
    response = _request("Please classify this ticket")
    trace = response.json()["trace"]
    assert response.status_code == 200
    assert trace["jev_error"] == "Jev offline"
    assert trace["routing_path"] == "jev_error -> strategy_fallback"
    assert len(trace["nodes"]) == 1
