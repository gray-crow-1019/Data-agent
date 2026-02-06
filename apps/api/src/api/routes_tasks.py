from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from api.deps import task_repo_dep, verify_auth
from orchestrator.engine import run
from settings import get_settings
from shared.types import TaskResponse, TaskSpec
from shared.utils import new_id
from tools.python.runtime import load_df, analyze_dataframe, preprocess_full
from tools.export.dataset_csv import export_csv
from shared.types import TaskResult

router = APIRouter()


@router.get("/tasks", response_model=list[TaskResponse], dependencies=[Depends(verify_auth)])
def list_tasks(
    repo=Depends(task_repo_dep),
    limit: int = Query(default=0, ge=0),
) -> list[TaskResponse]:
    settings = get_settings()
    if limit <= 0:
        limit = settings.task_history_limit
    records = repo.list(limit=limit)
    return [TaskResponse(spec=record.spec, result=record.result) for record in records]


@router.get("/tasks/{task_id}", response_model=TaskResponse, dependencies=[Depends(verify_auth)])
def get_task(task_id: str, repo=Depends(task_repo_dep)) -> TaskResponse:
    record = repo.get(task_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskResponse(spec=record.spec, result=record.result)


@router.post("/tasks/{task_id}/rerun", response_model=TaskResponse, dependencies=[Depends(verify_auth)])
def rerun_task(task_id: str, repo=Depends(task_repo_dep)) -> TaskResponse:
    record = repo.get(task_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    spec = TaskSpec(
        id=new_id(),
        question=record.spec.question,
        meta=record.spec.meta,
        labels=record.spec.labels,
    )
    repo.create(spec)
    result = run(spec)
    spec.status = "completed"
    repo.set_result(spec.id, result)
    return TaskResponse(spec=spec, result=result)


@router.delete("/tasks/{task_id}", dependencies=[Depends(verify_auth)])
def delete_task(task_id: str, repo=Depends(task_repo_dep)):
    if not repo.delete(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return {"status": "deleted"}


@router.get(
    "/tasks/{task_id}/artifacts/{kind}",
    dependencies=[Depends(verify_auth)],
)
def get_artifact(task_id: str, kind: str, repo=Depends(task_repo_dep)):
    record = repo.get(task_id)
    if not record or not record.result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    settings = get_settings()
    if kind in {"dataset_csv", "processed_csv", "processed_full_csv"} and not settings.allow_detail_export:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Detail export disabled")
    if kind == "processed_full_csv":
        dataset_profile = record.result.dataset_profile or {}
        table = dataset_profile.get("table")
        if not table:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dataset table not found")
        df = load_df(table, limit=2000000)
        summary = analyze_dataframe(df)
        processed = preprocess_full(df, summary)
        return {"kind": kind, "payload": export_csv({"rows": processed.to_dict(orient="records")})}
    artifact = record.result.artifacts.get(kind)
    if artifact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found")
    return {"kind": kind, "payload": artifact}


@router.get("/tasks/{task_id}/steps/{step_name}/download", dependencies=[Depends(verify_auth)])
def download_step_output(task_id: str, step_name: str, repo=Depends(task_repo_dep)):
    record = repo.get(task_id)
    if not record or not record.result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    step_outputs = (record.result.artifacts or {}).get("step_outputs", {})
    payload = step_outputs.get(step_name)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Step output not found")
    return {"kind": "step_output", "payload": payload}


@router.post("/tasks/{task_id}/charts", dependencies=[Depends(verify_auth)])
def add_custom_chart(task_id: str, payload: dict = Body(...), repo=Depends(task_repo_dep)):
    record = repo.get(task_id)
    if not record or not record.result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    chart = payload.get("chart")
    if not chart:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing chart")
    result = record.result
    result.charts = result.charts + [chart]
    repo.set_result(task_id, result)
    return {"status": "ok", "charts": result.charts}
