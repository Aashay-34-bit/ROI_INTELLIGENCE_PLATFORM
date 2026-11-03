from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter

from app.core.schemas import Trace


@contextmanager
def record_span(trace: Trace, name: str) -> Iterator[None]:
    start = perf_counter()
    try:
        yield
    finally:
        trace.events.append({"span": name, "duration_ms": (perf_counter() - start) * 1000})
