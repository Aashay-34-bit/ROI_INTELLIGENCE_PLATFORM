import time

from app.core.schemas import Node, NodeResult
from app.providers.registry import ModelRegistry
from app.validation.escalation import EscalationManager
from app.validation.retry_manager import RetryManager
from app.validation.validators import SchemaValidator


class TaskExecutor:
    def __init__(self, registry: ModelRegistry, retry_manager: RetryManager | None = None) -> None:
        self.registry = registry
        self.retry_manager = retry_manager or RetryManager()
        self.validator = SchemaValidator()
        self.escalation = EscalationManager()

    async def execute(self, node: Node, context: dict[str, str]) -> NodeResult:
        spec = self.registry.get(node.model_id or "mock-small-fp8")
        prompt = node.input or node.task
        if context:
            prompt += "\nParent outputs: " + str(context)
        precision = node.precision or spec.precisions[0]
        attempts = 0
        escalation_count = 0
        attempt_trace: list[str] = []
        while True:
            attempts += 1
            adapter = self.registry.adapter(spec.id)
            start = time.perf_counter()
            try:
                output = await adapter.generate(
                    prompt, precision, category=node.task_category.value
                )
                latency = (time.perf_counter() - start) * 1000
                validation = self.validator.validate(
                    node.task_category.value, output, node.required_fields
                )
                if not validation.valid:
                    raise ValueError("; ".join(validation.errors))
                attempt_trace.append(f"{attempts}:{spec.id}:{precision.value}:validated")
                in_tokens, out_tokens = max(1, len(prompt.split())), max(1, len(output.split()))
                cost = (in_tokens * spec.cost_per_1k_in + out_tokens * spec.cost_per_1k_out) / 1000
                return NodeResult(
                    node_id=node.node_id,
                    output=output,
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                    cost_usd=cost,
                    latency_ms=latency,
                    model_id=spec.id,
                    provider=spec.provider,
                    tier=spec.tier,
                    is_edge=spec.provider == "ollama",
                    precision=precision,
                    attempts=attempts,
                    escalation_count=escalation_count,
                    attempt_trace=attempt_trace,
                )
            except Exception as error:
                attempt_trace.append(f"{attempts}:{spec.id}:{precision.value}:failed:{error}")
                if self.retry_manager.consume(node.node_id):
                    continue
                next_model = self.escalation.next_model(
                    spec, self.registry.list(), node.task_category.value
                )
                if next_model is None:
                    raise
                escalation_count += 1
                spec, precision = next_model, next_model.precisions[0]
