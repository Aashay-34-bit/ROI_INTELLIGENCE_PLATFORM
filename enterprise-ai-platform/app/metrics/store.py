import json
import sqlite3
from pathlib import Path

from app.core.schemas import MetricRecord


class MetricStore:
    def __init__(self, path: str = "platform.db") -> None:
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS metrics (request_id TEXT PRIMARY KEY, created_at TEXT, category TEXT, cost REAL, latency REAL, successful INTEGER, payload TEXT)"
            )

    def write(self, record: MetricRecord) -> None:
        data = record.model_dump(mode="json")
        with sqlite3.connect(self.path) as db:
            db.execute(
                "INSERT OR REPLACE INTO metrics VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    record.request_id,
                    data["created_at"],
                    record.task_category.value,
                    record.cost_usd,
                    record.latency_ms,
                    int(record.successful),
                    json.dumps(data),
                ),
            )

    def all(self) -> list[MetricRecord]:
        with sqlite3.connect(self.path) as db:
            rows = db.execute("SELECT payload FROM metrics ORDER BY created_at").fetchall()
        return [MetricRecord.model_validate_json(row[0]) for row in rows]
