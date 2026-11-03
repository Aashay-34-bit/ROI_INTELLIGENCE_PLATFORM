from functools import lru_cache

from app.metrics.store import MetricStore
from app.providers.registry import ModelRegistry
from app.routing.precision_policy import PrecisionPolicy
from app.routing.router import Router


@lru_cache
def get_registry() -> ModelRegistry:
    return ModelRegistry()


@lru_cache
def get_policy() -> PrecisionPolicy:
    return PrecisionPolicy()


@lru_cache
def get_router() -> Router:
    from app.settings import get_settings

    return Router(get_registry(), get_policy(), get_settings().default_strategy)


@lru_cache
def get_store() -> MetricStore:
    from app.settings import get_settings

    url = get_settings().database_url
    path = url.removeprefix("sqlite:///") if url.startswith("sqlite:///") else "platform.db"
    return MetricStore(path)
