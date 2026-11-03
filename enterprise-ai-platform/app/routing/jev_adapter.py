from typing import Protocol, TypedDict


class Decision(TypedDict):
    choice: str
    confidence: float


class JevAdapter(Protocol):
    async def decide(self, input: str, questions: dict[str, list[str]]) -> dict[str, Decision]: ...

    def applies_to(self, task_category: str) -> bool: ...
