from typing import Protocol

from app.core.enums import PrecisionTier
from app.core.schemas import ModelSpec


class ProviderAdapter(Protocol):
    spec: ModelSpec

    async def generate(self, prompt: str, precision: PrecisionTier, **kwargs: object) -> str: ...
