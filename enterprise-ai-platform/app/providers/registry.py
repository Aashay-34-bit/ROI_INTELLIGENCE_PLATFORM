from pathlib import Path

import yaml

from app.core.schemas import ModelSpec
from app.providers.mock_adapter import MockAdapter


class ModelRegistry:
    def __init__(self, path: str | Path = "config/models.yaml") -> None:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        self.models = {item["id"]: ModelSpec.model_validate(item) for item in data["models"]}

    def list(self) -> list[ModelSpec]:
        return list(self.models.values())

    def get(self, model_id: str) -> ModelSpec:
        return self.models[model_id]

    def adapter(self, model_id: str) -> MockAdapter:
        from app.settings import get_settings

        settings = get_settings()
        return MockAdapter(
            self.get(model_id),
            settings.mock_min_latency_ms,
            settings.mock_max_latency_ms,
            settings.mock_failure_rate,
        )
