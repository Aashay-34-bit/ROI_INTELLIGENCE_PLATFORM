from app.core.schemas import Node


class ContextManager:
    def context(self, node: Node, outputs: dict[str, str]) -> dict[str, str]:
        return {parent: outputs[parent] for parent in node.depends_on if parent in outputs}
