class PlatformError(Exception):
    """Base exception for errors safe to expose through the platform API."""


class CycleDetectedError(PlatformError):
    pass


class RetryBudgetExhausted(PlatformError):
    pass
