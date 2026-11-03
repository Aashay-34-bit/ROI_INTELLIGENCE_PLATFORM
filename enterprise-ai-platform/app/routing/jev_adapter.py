from typing import Protocol


class JevAdapter(Protocol):
    async def decide(
        self, input: str, questions: dict[str, list[str]]
    ) -> dict[str, dict[str, object]]: ...
