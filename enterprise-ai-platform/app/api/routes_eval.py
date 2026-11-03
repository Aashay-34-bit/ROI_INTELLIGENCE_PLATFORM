from fastapi import APIRouter

from app.edge.harness_optimizer import HarnessOptimizer
from app.eval.evaluator import Evaluator

router = APIRouter()


@router.post("/v1/eval/run")
async def eval_run(mode: str = "benchmark") -> dict[str, object]:
    if mode == "harness":
        harness = await HarnessOptimizer().optimize(Evaluator().tasks)
        return {"mode": "harness", "config": harness.model_dump(mode="json")}
    run = await Evaluator().run()
    return run.model_dump(mode="json")
