from dataclasses import dataclass
from typing import ClassVar

from app.core.errors import EdgeUnavailable
from app.core.schemas import ModelSpec, Node, Request


@dataclass(frozen=True)
class Placement:
    target: str
    rationale: str
    escalation_reason: str | None = None


class EdgeRouter:
    EDGE_CAPABLE: ClassVar[frozenset[str]] = frozenset({"classification", "extraction"})

    def place(self, request: Request, node: Node, local_model: ModelSpec | None) -> Placement:
        category = node.task_category.value
        if request.privacy == "strict" and category in self.EDGE_CAPABLE:
            if local_model is None:
                raise EdgeUnavailable("strict privacy requires a ready local model")
            return Placement("edge", "strict privacy: local model selected")
        if request.privacy == "strict" and category in {"reasoning", "generation"}:
            return Placement(
                "cloud",
                "category exceeds local edge capability; routed to configured cloud provider",
                "edge_capability_exceeded",
            )
        return Placement("cloud", "standard cloud placement")

    def decide(
        self,
        request: Request,
        node: Node,
        local_model: ModelSpec | None,
        tolerance: float = 0.05,
        force_local: bool = False,
    ) -> tuple[bool, str]:
        """Compatibility wrapper for the original edge decision API."""
        placement = self.place(request, node, local_model)
        if force_local and local_model:
            return True, "local execution forced by configuration"
        return placement.target == "edge", placement.rationale
