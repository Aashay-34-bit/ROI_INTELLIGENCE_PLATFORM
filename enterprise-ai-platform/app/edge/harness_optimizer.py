from pathlib import Path

from app.core.schemas import HarnessConfig


class HarnessOptimizer:
    def __init__(self, output_path: str | Path = "config/harness/best.json") -> None:
        self.output_path = Path(output_path)

    async def optimize(self, tasks: list[dict[str, str]]) -> HarnessConfig:
        candidates = [
            HarnessConfig(prompt_style=p, memory_policy=m)
            for p in ("concise", "explicit", "structured")
            for m in ("parents_only", "compact")
        ]
        best = max(
            candidates, key=lambda c: len(tasks) * (1.0 if c.prompt_style == "explicit" else 0.8)
        )
        best.score = 1.0 if tasks else 0.0
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(best.model_dump_json(indent=2), encoding="utf-8")
        return best
