from __future__ import annotations

from fastapi import Header, HTTPException, Request, status

from persistence.db import get_task_repo
from settings import get_settings
from shared.utils import new_id


def verify_auth(authorization: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if not settings.auth_token:
        return
    expected = f"Bearer {settings.auth_token}"
    if authorization != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


def get_request_id(request: Request) -> str:
    if hasattr(request.state, "request_id"):
        return request.state.request_id
    header_name = get_settings().request_id_header
    return request.headers.get(header_name) or new_id()


def task_repo_dep():
    return get_task_repo()
