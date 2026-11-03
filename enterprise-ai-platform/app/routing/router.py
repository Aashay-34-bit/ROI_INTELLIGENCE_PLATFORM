from app.core.schemas import Request, RoutingDecision
from app.providers.registry import ModelRegistry
from app.routing.precision_policy import PrecisionPolicy
from app.routing.strategies import STRATEGIES
from app.settings import get_settings


class Router:
    def __init__(
        self, registry: ModelRegistry, policy: PrecisionPolicy, default: str = "cost_quality"
    ) -> None:
        self.registry, self.policy, self.default = registry, policy, default

    def route(self, request: Request) -> RoutingDecision:
        strategy = STRATEGIES.get(request.strategy or self.default, STRATEGIES[self.default])
        candidates = self.registry.candidates(get_settings().model_provider.lower())
        if not candidates:
            raise ValueError(
                f"No models are configured for provider {get_settings().model_provider!r}"
            )
        return strategy.select(request, candidates, self.policy)
