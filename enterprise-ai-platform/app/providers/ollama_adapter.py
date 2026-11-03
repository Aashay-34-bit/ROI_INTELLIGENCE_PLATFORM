import httpx

from app.core.enums import PrecisionTier
from app.core.schemas import ModelSpec


class OllamaAdapter:
    def __init__(self, spec: ModelSpec, base_url: str = "http://localhost:11434") -> None:
        self.spec, self.base_url = spec, base_url.rstrip("/")

    async def generate(self, prompt: str, precision: PrecisionTier, **kwargs: object) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.spec.id, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            return response.json()["response"]
