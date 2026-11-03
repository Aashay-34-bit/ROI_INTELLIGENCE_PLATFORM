class RetryManager:
    def __init__(self, max_per_node: int = 2, max_per_request: int = 4) -> None:
        self.max_per_node, self.remaining = max_per_node, max_per_request
        self.node_attempts: dict[str, int] = {}

    def consume(self, node_id: str) -> bool:
        used = self.node_attempts.get(node_id, 0)
        if used >= self.max_per_node or self.remaining <= 0:
            return False
        self.node_attempts[node_id] = used + 1
        self.remaining -= 1
        return True
