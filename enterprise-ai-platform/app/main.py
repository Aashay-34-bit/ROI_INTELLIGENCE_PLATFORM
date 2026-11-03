from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import routes_eval, routes_gateway, routes_metrics, routes_models
from app.api.deps import get_registry
from app.core.errors import EdgeUnavailable, OllamaUnreachable
from app.core.logging import get_logger
from app.settings import get_settings

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.model_provider.lower() == "ollama":
        ready = await get_registry().preflight()
        if not ready:
            logger.error("Ollama provider preflight failed; requests will return HTTP 503")
    yield


app = FastAPI(title="Enterprise AI Intelligence & ROI Platform", version="0.1.0", lifespan=lifespan)
app.include_router(routes_gateway.router)
app.include_router(routes_metrics.router)
app.include_router(routes_models.router)
app.include_router(routes_eval.router)


@app.exception_handler(OllamaUnreachable)
async def ollama_unreachable_handler(request: Request, error: OllamaUnreachable) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"error": "ollama_unreachable", "detail": str(error)},
    )


@app.exception_handler(EdgeUnavailable)
async def edge_unavailable_handler(request: Request, error: EdgeUnavailable) -> JSONResponse:
    return JSONResponse(
        status_code=503, content={"error": "edge_unavailable", "detail": str(error)}
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
