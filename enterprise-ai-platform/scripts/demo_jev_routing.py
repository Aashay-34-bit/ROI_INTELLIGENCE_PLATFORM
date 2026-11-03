"""Show Jev gating a duplicate-charge request to the local billing rule."""

import json
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8014"


def main() -> None:
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8014"],
        cwd=ROOT,
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
                    "input": "I was charged twice for my subscription. Please refund.",
                    "task_category": "classification",
                },
            )
            response.raise_for_status()
            payload = response.json()
            trace = payload["trace"]
            assert trace["jev_decisions"]["refund_request"]["choice"] == "Yes", trace
            assert trace["routing_path"] == "jev_map:refund_request=Yes -> rule:billing_handler", (
                trace
            )
            assert trace["nodes"] == [], trace
            print(json.dumps(payload, indent=2))
    finally:
        server.terminate()
        server.wait(timeout=10)


if __name__ == "__main__":
    main()
