from __future__ import annotations

from pathlib import Path

import yaml

from app.core.errors import ProviderNotAvailable
from app.core.schemas import ModelSpec
from app.providers.anthropic_adapter import AnthropicAdapter
from app.providers.base import ProviderAdapter
from app.providers.mock_adapter import MockAdapter
from app.providers.ollama_adapter import OllamaAdapter
from app.providers.openai_adapter import OpenAIAdapter


class ModelRegistry:
    def __init__(self, path: str | Path = "config/models.yaml") -> None:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        self.models = {item["id"]: ModelSpec.model_validate(item) for item in data["models"]}
        self.provider_ready = True

    def list(self) -> list[ModelSpec]:
        return list(self.models.values())

    def candidates(self, provider_filter: str | None = None) -> list[ModelSpec]:
        if provider_filter is None:
            return self.list()
        return [model for model in self.models.values() if model.provider == provider_filter]

    def get(self, model_id: str) -> ModelSpec:
        return self.models[model_id]

    def adapter(self, model_id: str) -> ProviderAdapter:
        from app.settings import get_settings

        settings = get_settings()
        spec = self.get(model_id)
        provider = settings.model_provider.lower()
        if provider == "mock":
            return MockAdapter(
                spec,
                settings.mock_min_latency_ms,
                settings.mock_max_latency_ms,
                settings.mock_failure_rate,
            )
        if provider == "ollama":
            if spec.provider != "ollama":
                raise ProviderNotAvailable(model_id, spec.provider)
            return OllamaAdapter(spec, settings.ollama_base_url, self.provider_ready)
        if provider == "openai":
            if spec.provider != "openai" or not settings.openai_api_key:
                raise ProviderNotAvailable(model_id, spec.provider)
            return OpenAIAdapter(spec, settings.openai_api_key)
        if provider == "anthropic":
            if spec.provider != "anthropic" or not settings.anthropic_api_key:
                raise ProviderNotAvailable(model_id, spec.provider)
            return AnthropicAdapter(spec, settings.anthropic_api_key)
        raise ValueError(f"Unsupported MODEL_PROVIDER: {settings.model_provider!r}")

    async def preflight(self) -> bool:
        from app.settings import get_settings

        settings = get_settings()
        if settings.model_provider.lower() != "ollama":
            self.provider_ready = True
            return True
        models = self.candidates("ollama")
        if not models:
            self.provider_ready = False
            return False
        adapter = OllamaAdapter(models[0], settings.ollama_base_url)
        self.provider_ready = await adapter.preflight()
        return self.provider_ready
