from contextlib import contextmanager
from typing import Iterator


@contextmanager
def trace_span(name: str) -> Iterator[None]:
    # Placeholder for OpenTelemetry or similar.
    _ = name
    yield
