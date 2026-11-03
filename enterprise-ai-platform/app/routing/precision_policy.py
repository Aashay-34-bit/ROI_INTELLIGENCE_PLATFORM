from pathlib import Path

import yaml

from app.core.enums import PrecisionTier


class PrecisionPolicy:
    def __init__(self, path: str | Path = "config/precision_policy.yaml") -> None:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        self.default = PrecisionTier(data["default"])
        self.overrides = {
            key: PrecisionTier(value) for key, value in data["task_overrides"].items()
        }

    def select(self, category: str, model: object | None = None) -> PrecisionTier:
        return self.overrides.get(category, self.default)
