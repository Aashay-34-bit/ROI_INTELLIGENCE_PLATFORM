from app.core.schemas import MetricRecord
from app.metrics.store import MetricStore


class MetricsRecorder:
    def __init__(self, store: MetricStore) -> None:
        self.store = store

    def record(self, record: MetricRecord) -> None:
        self.store.write(record)
