from fastapi import APIRouter, Depends

from app.api.deps import get_store
from app.metrics.aggregator import summarize

router = APIRouter()


@router.get("/v1/metrics/summary")
async def metrics_summary(store=Depends(get_store)) -> dict[str, object]:  # noqa: B008
    return summarize(store.all())


@router.get("/v1/metrics/timeseries")
async def metrics_timeseries(store=Depends(get_store)) -> list[dict[str, object]]:  # noqa: B008
    buckets: dict[str, dict[str, float]] = {}
    for record in store.all():
        bucket = record.created_at.strftime("%Y-%m-%dT%H:00")
        data = buckets.setdefault(bucket, {"requests": 0, "cost_usd": 0})
        data["requests"] += 1
        data["cost_usd"] += record.cost_usd
    return [{"period": period, **values} for period, values in sorted(buckets.items())]
