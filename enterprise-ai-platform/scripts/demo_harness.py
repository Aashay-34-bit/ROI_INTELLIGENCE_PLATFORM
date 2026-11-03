import asyncio
import json

from app.edge.harness_optimizer import HarnessOptimizer
from app.eval.evaluator import Evaluator


async def main() -> None:
    task_set = Evaluator().tasks
    config = await HarnessOptimizer().optimize(
        task_set,
        base_config={"prompt_style": "baseline", "memory_policy": "parents_only"},
        candidates=[
            {"config_id": "baseline", "prompt_style": "baseline", "memory_policy": "parents_only"},
            {"config_id": "concise", "prompt_style": "concise", "memory_policy": "parents_only"},
            {"config_id": "few-shot", "prompt_style": "few_shot", "memory_policy": "parents_only"},
        ],
    )
    print(json.dumps(config.model_dump(mode="json"), indent=2))
    print("Persisted detailed result: config/harness/best.json")


if __name__ == "__main__":
    asyncio.run(main())
