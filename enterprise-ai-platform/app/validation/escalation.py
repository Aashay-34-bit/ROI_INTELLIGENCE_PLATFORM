from typing import ClassVar

from app.core.schemas import ModelSpec


class EscalationManager:
    _tier: ClassVar[dict[str, int]] = {"small": 0, "medium": 1, "advanced": 2}

    def next_model(
        self, current: ModelSpec, models: list[ModelSpec], category: str
    ) -> ModelSpec | None:
        eligible = [
            m
            for m in models
            if self._tier.get(m.tier, 0) > self._tier.get(current.tier, 0)
            and category in m.capability_tags
        ]
        return min(eligible, key=lambda m: m.cost_per_1k_in + m.cost_per_1k_out, default=None)
