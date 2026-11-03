from enum import StrEnum


class PrecisionTier(StrEnum):
    FP8 = "fp8"
    AWQ4 = "awq4"
    FP16 = "fp16"


class TaskCategory(StrEnum):
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"
    REASONING = "reasoning"
    GENERATION = "generation"
    SAFETY_CRITICAL = "safety_critical"
    COMPUTATION = "computation"


class RequestStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
