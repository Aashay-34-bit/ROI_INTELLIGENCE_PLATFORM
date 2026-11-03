from app.core.schemas import Request, RoutingDecision
from app.providers.registry import ModelRegistry
from app.routing.precision_policy import PrecisionPolicy
from app.routing.strategies import STRATEGIES


class Router:
    def __init__(
        self, registry: ModelRegistry, policy: PrecisionPolicy, default: str = "cost_quality"
    ) -> None:
        self.registry, self.policy, self.default = registry, policy, default

    def route(self, request: Request) -> RoutingDecision:
        strategy = STRATEGIES.get(request.strategy or self.default, STRATEGIES[self.default])
        return strategy.select(request, self.registry.list(), self.policy)
