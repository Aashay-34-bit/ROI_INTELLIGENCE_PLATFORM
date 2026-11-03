class PlatformError(Exception):
    """Base exception for errors safe to expose through the platform API."""


class CycleDetectedError(PlatformError):
    pass


class RetryBudgetExhausted(PlatformError):
    pass


class ProviderNotAvailable(PlatformError):
    def __init__(self, model_id: str, provider: str) -> None:
        self.model_id = model_id
        self.provider = provider
        super().__init__(
            f"Model {model_id!r} uses provider {provider!r}, not the configured provider"
        )


class OllamaUnreachable(PlatformError):
    pass


class EdgeUnavailable(PlatformError):
    pass


class TaskExecutionFailed(PlatformError):
    pass
