from fastapi import APIRouter, Depends

from app.api.deps import get_registry

router = APIRouter()


@router.get("/v1/models")
async def models(registry=Depends(get_registry)) -> list[dict[str, object]]:  # noqa: B008
    return [m.model_dump(mode="json") for m in registry.list()]
