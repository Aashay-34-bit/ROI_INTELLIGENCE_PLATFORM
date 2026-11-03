from pathlib import Path

import yaml


class JevMockBackend:
    def __init__(self, router_config: str | Path = "config/router.yaml") -> None:
        self.router_config = yaml.safe_load(Path(router_config).read_text(encoding="utf-8"))

    def applies_to(self, task_category: str) -> bool:
        return task_category in self.router_config.get("jev_applies_to", [])

    async def decide(
        self, input: str, questions: dict[str, list[str]]
    ) -> dict[str, dict[str, object]]:
        text = input.lower()
        output: dict[str, dict[str, object]] = {}
        for key, choices in questions.items():
            if key == "refund_request":
                affirmative = any(
                    phrase in text for phrase in ("charged twice", "refund", "duplicate charge")
                )
                desired = "yes" if affirmative else "no"
                choice = next((x for x in choices if x.lower() == desired), choices[0])
            elif key == "urgency":
                urgent = any(word in text for word in ("urgent", "immediately", "critical"))
                desired = "high" if urgent else "normal"
                choice = next((x for x in choices if x.lower() == desired), choices[0])
            elif key == "category":
                billing = any(word in text for word in ("charged", "billing", "refund"))
                desired = "billing" if billing else "general"
                choice = next((x for x in choices if x.lower() == desired), choices[-1])
            else:
                choice = next((x for x in choices if x.lower() in text), choices[0])
            output[key] = {"choice": choice, "confidence": 0.75}
        return output


class JevHTTPBackend:
    def __init__(self, base_url: str | None) -> None:
        self.base_url = base_url

    async def decide(
        self, input: str, questions: dict[str, list[str]]
    ) -> dict[str, dict[str, object]]:
        if not self.base_url:
            raise RuntimeError("JEV_BASE_URL is not configured")
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url, json={"input": input, "questions": questions}
            )
            response.raise_for_status()
            return response.json()
