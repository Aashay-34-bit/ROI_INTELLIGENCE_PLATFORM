"""Run an isolated local API demo of deterministic retry and escalation."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8013"


def main() -> None:
    env = os.environ.copy()
    env.update(
        MODEL_PROVIDER="mock",
        MOCK_MODE="flaky_first",
        MOCK_FAIL_FIRST_MODEL="mock-small-fp8",
        MAX_RETRIES_PER_NODE="0",
        MAX_RETRIES_PER_REQUEST="0",
    )
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8013"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        with httpx.Client(timeout=20) as client:
            for _ in range(60):
                try:
                    if client.get(f"{BASE}/health").status_code == 200:
                        break
                except httpx.HTTPError:
                    time.sleep(0.25)
            else:
                raise RuntimeError("demo API did not start")
            response = client.post(
                f"{BASE}/v1/request",
                headers={"X-API-Key": "demo-key"},
                json={
                    "input": "Write a short description of this demo",
                    "task_category": "generation",
                },
            )
            response.raise_for_status()
            request_id = response.json()["request_id"]
            trace = client.get(f"{BASE}/v1/request/{request_id}").json()["trace"]
            matching = [node for node in trace["nodes"] if node["attempts"] == 2]
            assert len(matching) == 1, trace
            assert matching[0]["escalated"] is True, trace
            assert matching[0]["escalated_from"], trace
            print(json.dumps(trace, indent=2))
            print(f"Trace request: {BASE}/v1/request/{request_id}")
    finally:
        server.terminate()
        server.wait(timeout=10)


if __name__ == "__main__":
    main()
