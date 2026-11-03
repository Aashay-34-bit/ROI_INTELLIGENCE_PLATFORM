"""Opt-in smoke test against an Ollama server running on this machine."""

import os

os.environ["MODEL_PROVIDER"] = "ollama"

from fastapi.testclient import TestClient

from app.main import app


def main() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/request",
            headers={"X-API-Key": os.getenv("API_KEY", "demo-key")},
            json={
                "input": "Classify this message as positive or negative: the service was excellent",
                "task_category": "classification",
            },
        )
        response.raise_for_status()
        trace = response.json()["trace"]
        node = trace["nodes"][0]
        assert node["provider"] == "ollama", trace
        assert node["model_id"] == "qwen3.5:4b", trace
        print({"provider": node["provider"], "model_id": node["model_id"], "trace": trace})


if __name__ == "__main__":
    main()
