from app.core.schemas import Request


class ComplexityScorer:
    def score(self, request: Request, required_fields: int = 0) -> int:
        # Length contributes only modestly: structured constraints and reasoning intent drive complexity.
        score = 1 + min(2, len(request.input.split()) // 80) + min(3, required_fields)
        if request.task_category.value in {"reasoning", "safety_critical"}:
            score += 3
        elif request.task_category.value in {"generation", "extraction"}:
            score += 1
        if any(
            word in request.input.lower()
            for word in ("compare", "tradeoff", "step by step", "multiple")
        ):
            score += 2
        return min(10, score)
