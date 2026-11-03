from app.core.schemas import ModelSpec, Node, Request


class EdgeRouter:
    def decide(
        self,
        request: Request,
        node: Node,
        local_model: ModelSpec | None,
        tolerance: float = 0.05,
        force_local: bool = False,
    ) -> tuple[bool, str]:
        if request.privacy == "strict":
            return (local_model is not None, "strict privacy requires local execution")
        if force_local and local_model:
            return True, "local execution forced by configuration"
        if node.task_category.value in {"classification", "extraction"} and local_model:
            delta = abs(local_model.quant_accuracy_delta.get(node.task_category.value, 1.0))
            return (
                (True, "local quality delta is within tolerance")
                if delta <= tolerance
                else (False, "local quality delta exceeds tolerance")
            )
        return False, "reasoning and generation prefer cloud execution"
