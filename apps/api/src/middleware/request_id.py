from __future__ import annotations

from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from settings import get_settings
from shared.utils import new_id


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        settings = get_settings()
        header_name = settings.request_id_header
        request_id = request.headers.get(header_name) or new_id()
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[header_name] = request_id
        return response
