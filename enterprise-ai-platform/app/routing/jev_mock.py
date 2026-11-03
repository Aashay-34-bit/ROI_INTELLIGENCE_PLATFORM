class JevMockBackend:
    async def decide(
        self, input: str, questions: dict[str, list[str]]
    ) -> dict[str, dict[str, object]]:
        text = input.lower()
        output: dict[str, dict[str, object]] = {}
        for key, choices in questions.items():
            if key == "urgency":
                choice = next(
                    (x for x in choices if x.lower() in text and x.lower() in {"high", "urgent"}),
                    choices[0],
                )
            elif key == "refund_request":
                choice = next((x for x in choices if x.lower() in text), choices[-1])
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
