from app.core.schemas import ModelSpec, Request, RoutingDecision


class BaseRouterStrategy:
    name = "base"

    def select(
        self, request: Request, candidates: list[ModelSpec], policy: object
    ) -> RoutingDecision:
        raise NotImplementedError


class CostQualityRouter(BaseRouterStrategy):
    name = "cost_quality"

    def select(
        self, request: Request, candidates: list[ModelSpec], policy: object
    ) -> RoutingDecision:
        acceptable = [
            m
            for m in candidates
            if request.task_category.value in m.capability_tags
            and m.quality
            >= {
                "classification": 0.85,
                "extraction": 0.90,
                "reasoning": 0.95,
                "generation": 0.90,
                "safety_critical": 0.99,
                "computation": 0.8,
            }[request.task_category.value]
        ]
        pool = acceptable or [m for m in candidates if m.tier != "advanced"] or candidates
        model = min(pool, key=lambda m: m.cost_per_1k_in + m.cost_per_1k_out)
        precision = policy.select(request.task_category.value, model)
        if precision not in model.precisions:
            precision = model.precisions[0]
        return RoutingDecision(
            model_id=model.id,
            precision=precision,
            strategy=self.name,
            rationale="lowest-cost eligible model",
        )


class RuleBasedRouter(CostQualityRouter):
    name = "rule_based"


class ComplexityBasedRouter(CostQualityRouter):
    name = "complexity_based"

    def select(
        self, request: Request, candidates: list[ModelSpec], policy: object
    ) -> RoutingDecision:
        if request.task_category.value in {"reasoning", "safety_critical"}:
            models = sorted(candidates, key=lambda m: (m.tier == "advanced", m.quality))
            model = next(
                (
                    m
                    for m in models
                    if m.quality >= 0.95 and request.task_category.value in m.capability_tags
                ),
                models[-1],
            )
            precision = policy.select(request.task_category.value, model)
            if precision not in model.precisions:
                precision = model.precisions[0]
            return RoutingDecision(
                model_id=model.id,
                precision=precision,
                strategy=self.name,
                rationale="higher complexity quality bar",
            )
        return super().select(request, candidates, policy)


class ConfidenceBasedRouter(CostQualityRouter):
    name = "confidence_based"


STRATEGIES = {
    s.name: s()
    for s in (RuleBasedRouter, ComplexityBasedRouter, ConfidenceBasedRouter, CostQualityRouter)
}
