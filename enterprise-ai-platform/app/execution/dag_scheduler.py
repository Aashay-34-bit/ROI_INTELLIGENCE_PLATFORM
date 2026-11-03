import asyncio

from app.core.errors import OllamaUnreachable, TaskExecutionFailed
from app.core.schemas import Plan, Trace
from app.execution.context_manager import ContextManager
from app.execution.task_executor import TaskExecutor


class DAGScheduler:
    def __init__(self, executor: TaskExecutor) -> None:
        self.executor = executor
        self.context_manager = ContextManager()

    @staticmethod
    def critical_path(
        plan: Plan, durations: dict[str, float] | None = None
    ) -> tuple[list[str], float]:
        nodes = {n.node_id: n for n in plan.nodes}
        if len(nodes) != len(plan.nodes):
            raise ValueError("duplicate node id")
        memo: dict[str, tuple[float, list[str]]] = {}
        visiting: set[str] = set()

        def visit(node_id: str) -> tuple[float, list[str]]:
            if node_id in visiting:
                raise ValueError("cycle detected in plan")
            if node_id in memo:
                return memo[node_id]
            visiting.add(node_id)
            node = nodes[node_id]
            parents = [visit(parent) for parent in node.depends_on]
            best = max(parents, default=(0.0, []), key=lambda x: x[0])
            result = (best[0] + (durations or {}).get(node_id, 0.0), best[1] + [node_id])
            visiting.remove(node_id)
            memo[node_id] = result
            return result

        for node in plan.nodes:
            for parent in node.depends_on:
                if parent not in nodes:
                    raise ValueError(f"unknown dependency {parent}")
            visit(node.node_id)
        leaves = [
            node_id for node_id in nodes if not any(node_id in n.depends_on for n in nodes.values())
        ]
        best = max((memo[node_id] for node_id in leaves), key=lambda x: x[0], default=(0.0, []))
        return best[1], best[0]

    async def schedule(self, plan: Plan, request_id: str = "") -> Trace:
        nodes = {n.node_id: n for n in plan.nodes}
        self.critical_path(plan)
        outputs: dict[str, str] = {}
        results = []
        pending = set(nodes)
        execution_waves = 0
        while pending:
            ready = [nodes[n] for n in pending if all(p in outputs for p in nodes[n].depends_on)]
            if not ready:
                raise ValueError("cycle detected in plan")
            execution_waves += 1
            completed = await asyncio.gather(
                *(
                    self.executor.execute(node, self.context_manager.context(node, outputs))
                    for node in ready
                ),
                return_exceptions=True,
            )
            for node, result in zip(ready, completed, strict=True):
                pending.remove(node.node_id)
                if isinstance(result, BaseException):
                    if isinstance(result, OllamaUnreachable):
                        raise result
                    raise TaskExecutionFailed(f"node {node.node_id} failed: {result}") from result
                outputs[node.node_id] = str(result.output)
                results.append(result)
        path, duration = self.critical_path(plan, {r.node_id: r.latency_ms for r in results})
        for result in results:
            result.critical_path_member = result.node_id in path
        trace = Trace(
            request_id=request_id,
            nodes=results,
            critical_path_latency_ms=duration,
            critical_path_length=len(path),
        )
        trace.retry_count = sum(max(0, result.attempts - 1) for result in results)
        trace.escalation_count = sum(result.escalation_count for result in results)
        trace.parallel_efficiency = len(results) / max(1, execution_waves * len(results))
        trace.events.append({"critical_path": path})
        trace.events.extend(
            {"node_id": result.node_id, "attempts": result.attempt_trace} for result in results
        )
        return trace
