import asyncio
import hashlib
import random
import re

from app.core.enums import PrecisionTier
from app.core.schemas import ModelSpec


class MockAdapter:
    def __init__(
        self,
        spec: ModelSpec,
        min_latency_ms: int = 0,
        max_latency_ms: int = 0,
        failure_rate: float = 0.0,
    ) -> None:
        self.spec = spec
        self.min_latency_ms = min_latency_ms
        self.max_latency_ms = max_latency_ms
        self.failure_rate = failure_rate

    async def health(self) -> bool:
        return True

    async def generate(self, prompt: str, precision: PrecisionTier, **kwargs: object) -> str:
        seed = int(hashlib.sha256((self.spec.id + prompt).encode()).hexdigest()[:8], 16)
        rng = random.Random(seed)
        if self.max_latency_ms:
            await asyncio.sleep(rng.randint(self.min_latency_ms, self.max_latency_ms) / 1000)
        if rng.random() < self.failure_rate:
            raise RuntimeError("simulated provider failure")
        category = str(kwargs.get("category", "generation"))
        text = prompt.lower()
        if category == "classification":
            label = (
                "positive"
                if any(word in text for word in ("great", "good", "excellent"))
                else "negative"
                if any(word in text for word in ("bad", "terrible", "awful"))
                else "question"
                if "?" in prompt
                else "neutral"
            )
            return label
        if category == "extraction":
            email = re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", prompt)
            if email:
                return email.group(0)
            phone = re.search(r"\b\+?[\d ()-]{7,}\b", prompt)
            if phone:
                return phone.group(0).strip()
            name = re.search(r"(?:name\s*:\s*)([A-Za-z ]+)", prompt, re.IGNORECASE)
            return name.group(1).strip() if name else "No extractable value"
        if category == "reasoning":
            return f"Reasoning summary: {prompt[:400]}"
        return f"Hello! Here is a concise response: {prompt[:400]}"
