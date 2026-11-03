from fastapi import FastAPI

from app.api import routes_eval, routes_gateway, routes_metrics, routes_models

app = FastAPI(title="Enterprise AI Intelligence & ROI Platform", version="0.1.0")
app.include_router(routes_gateway.router)
app.include_router(routes_metrics.router)
app.include_router(routes_models.router)
app.include_router(routes_eval.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
