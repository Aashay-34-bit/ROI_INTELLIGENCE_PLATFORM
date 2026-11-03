from fastapi import APIRouter, Depends, Header, HTTPException

from app.api.deps import get_registry, get_router, get_store
from app.core.enums import RequestStatus, TaskCategory
from app.core.schemas import MetricRecord, Node, Plan, Request, RequestResponse, Trace
from app.execution.dag_scheduler import DAGScheduler
from app.execution.task_executor import TaskExecutor
from app.routing.jev_mock import JevMockBackend
from app.routing.rule_engine import RuleEngine
from app.settings import get_settings

router = APIRouter()
REQUESTS: dict[str, RequestResponse] = {}


@router.post("/v1/request", response_model=RequestResponse)
async def submit_request(
    body: Request,
    x_api_key: str | None = Header(default=None),
    routing=Depends(get_router),  # noqa: B008
    registry=Depends(get_registry),  # noqa: B008
    store=Depends(get_store),  # noqa: B008
) -> RequestResponse:
    if x_api_key != get_settings().api_key:
        raise HTTPException(status_code=401, detail="invalid API key")
    rule_field = (
        "email" if body.task_category == TaskCategory.EXTRACTION and "@" in body.input else None
    )
    rule_result = RuleEngine().handle(body.task_category.value, body.input, rule_field)
    bounded_decisions = await JevMockBackend().decide(
        body.input,
        {"urgency": ["high", "normal"], "refund_request": ["refund", "no_refund"]},
    )
    if rule_result is not None:
        trace = Trace(
            request_id=body.request_id,
            events=[{"route": "rule", "result": rule_result}, {"jev": bounded_decisions}],
        )
        result = rule_result
    else:
        supplied_nodes = body.metadata.get("subtasks")
        if supplied_nodes:
            plan = Plan(nodes=[Node.model_validate(item) for item in supplied_nodes])
        else:
            plan = Plan(
                nodes=[
                    Node(
                        node_id="main",
                        task=body.input,
                        input=body.input,
                        task_category=body.task_category,
                    )
                ]
            )
        decisions = {}
        for node in plan.nodes:
            node_request = body.model_copy(
                update={"input": node.input or node.task, "task_category": node.task_category}
            )
            decision = routing.route(node_request)
            node.model_id = node.model_id or decision.model_id
            node.precision = node.precision or decision.precision
            decisions[node.node_id] = {
                "model_id": node.model_id,
                "strategy": decision.strategy,
                "precision": node.precision.value,
            }
        trace = await DAGScheduler(TaskExecutor(registry)).schedule(plan, body.request_id)
        trace.events.extend([{"routes": decisions}, {"jev": bounded_decisions}])
        result = (
            trace.nodes[0].output
            if len(trace.nodes) == 1
            else {
                node.node_id: next(
                    (r.output for r in trace.nodes if r.node_id == node.node_id), None
                )
                for node in plan.nodes
            }
        )
    metric = MetricRecord(
        request_id=body.request_id,
        user_id=body.user_id,
        task_category=body.task_category,
        strategy_used=body.strategy or get_settings().default_strategy,
        nodes=[n.model_dump(mode="json") for n in trace.nodes],
        input_tokens=sum(n.input_tokens for n in trace.nodes),
        output_tokens=sum(n.output_tokens for n in trace.nodes),
        cost_usd=sum(n.cost_usd for n in trace.nodes),
        latency_ms=sum(n.latency_ms for n in trace.nodes),
        critical_path_latency_ms=trace.critical_path_latency_ms,
        parallel_efficiency=trace.parallel_efficiency,
        retry_count=trace.retry_count,
        escalation_count=trace.escalation_count,
        jev_decision_count=len(bounded_decisions),
        jev_decisions_covered=len(bounded_decisions),
        quantization_accuracy_delta={
            node.model_id: registry.get(node.model_id).quant_accuracy_delta.get(
                body.task_category.value, 0.0
            )
            for node in trace.nodes
        },
        successful=True,
    )
    store.write(metric)
    response = RequestResponse(
        request_id=body.request_id, status=RequestStatus.SUCCEEDED, result=result, trace=trace
    )
    REQUESTS[body.request_id] = response
    return response


@router.get("/v1/request/{request_id}", response_model=RequestResponse)
async def request_status(request_id: str) -> RequestResponse:
    if request_id not in REQUESTS:
        raise HTTPException(status_code=404, detail="request not found")
    return REQUESTS[request_id]
