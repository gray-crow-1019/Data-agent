from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Callable, Deque, Dict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from settings import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app) -> None:
        super().__init__(app)
        self._buckets: Dict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        settings = get_settings()
        rps = max(settings.rate_limit_rps, 1)
        key = request.client.host if request.client else "unknown"
        now = time.time()
        bucket = self._buckets[key]
        while bucket and now - bucket[0] > 1.0:
            bucket.popleft()
        if len(bucket) >= rps:
            return JSONResponse(status_code=429, content={"detail": "Rate limited"})
        bucket.append(now)
        return await call_next(request)
