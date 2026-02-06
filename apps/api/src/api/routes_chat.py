from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.deps import get_request_id, task_repo_dep, verify_auth
from orchestrator.engine import run
from shared.types import ClarifyParams, TaskResult, TaskSpec
from shared.utils import new_id

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    metadata: Optional[Dict[str, Any]] = None
    clarify: Optional[ClarifyParams] = None
    labels: Optional[list[str]] = None


class ChatResponse(BaseModel):
    task_id: str
    result: TaskResult


@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(verify_auth)])
def chat(
    payload: ChatRequest,
    repo=Depends(task_repo_dep),
    request_id: str = Depends(get_request_id),
) -> ChatResponse:
    meta = {"request_id": request_id}
    if payload.metadata:
        meta.update(payload.metadata)
    spec = TaskSpec(id=new_id(), question=payload.question, meta=meta, labels=payload.labels or [])
    repo.create(spec)
    result = run(spec)
    spec.status = "completed"
    if payload.clarify:
        result.clarify = payload.clarify
    repo.set_result(spec.id, result)
    return ChatResponse(task_id=spec.id, result=result)
