import asyncio

from app.core.enums import TaskCategory
from app.core.schemas import Node, Plan
from app.execution.dag_scheduler import DAGScheduler
from app.execution.task_executor import TaskExecutor
from app.providers.mock_adapter import MockAdapter
from app.providers.registry import ModelRegistry


def test_critical_path_and_cycle_detection() -> None:
    scheduler = DAGScheduler(TaskExecutor(ModelRegistry()))
    plan = Plan(
        nodes=[
            Node(node_id="a", task="a", task_category=TaskCategory.GENERATION),
            Node(node_id="b", task="b", task_category=TaskCategory.GENERATION, depends_on=["a"]),
        ]
    )
    assert scheduler.critical_path(plan)[0] == ["a", "b"]
    plan.nodes[0].depends_on = ["b"]
    try:
        scheduler.critical_path(plan)
    except ValueError as error:
        assert "cycle" in str(error)
    else:
        raise AssertionError("cycle was not detected")


async def test_independent_nodes_run_concurrently() -> None:
    registry = ModelRegistry()
    registry.adapter = lambda model_id: MockAdapter(registry.get(model_id))
    scheduler = DAGScheduler(TaskExecutor(registry))
    plan = Plan(
        nodes=[
            Node(node_id=str(i), task="parallel", task_category=TaskCategory.GENERATION)
            for i in range(3)
        ]
    )
    trace = await asyncio.wait_for(scheduler.schedule(plan), timeout=5)
    assert len(trace.nodes) == 3
    assert trace.parallel_efficiency >= 0.6
