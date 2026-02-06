from __future__ import annotations

import os
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Body

from api.deps import verify_auth
from settings import get_settings
from shared.utils import new_id
from persistence.datasets import add_dataset, list_datasets as list_dataset_store
from tools.sql.loader import DatasetLoadError, load_dataset_to_db
from tools.python.runtime import load_df, analyze_dataframe, build_charts_from_plan
from tools.export.dataset_csv import export_csv

router = APIRouter()



def _save_upload(file: UploadFile, uploads_dir: str, file_id: str) -> str:
    os.makedirs(uploads_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1].lower() or ".csv"
    target = os.path.join(uploads_dir, f"{file_id}{ext}")
    with open(target, "wb") as handle:
        handle.write(file.file.read())
    return target


@router.post("/datasets/upload", dependencies=[Depends(verify_auth)])
def upload_dataset(file: UploadFile = File(...)):
    settings = get_settings()
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing file")
    if not any(file.filename.lower().endswith(ext) for ext in [".csv", ".xlsx", ".xls", ".mat"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

    content = file.file.read()
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")

    uploads_dir = settings.uploads_dir
    os.makedirs(uploads_dir, exist_ok=True)
    file_id = new_id()
    # Rewind file and persist with original extension for correct parsing.
    file.file.seek(0)
    target = _save_upload(file, uploads_dir, file_id)

    table_name = f"uploaded_{file_id}"
    try:
        columns, row_count = load_dataset_to_db(target, table_name)
    except DatasetLoadError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    record = {
        "id": file_id,
        "filename": file.filename,
        "table": table_name,
        "columns": columns,
        "row_count": row_count,
        "created_at": datetime.utcnow().isoformat(),
    }
    add_dataset(record)
    return record


@router.get("/datasets", dependencies=[Depends(verify_auth)])
def list_datasets():
    return list_dataset_store()


@router.get("/datasets/{dataset_id}/download", dependencies=[Depends(verify_auth)])
def download_dataset(dataset_id: str):
    datasets = list_dataset_store()
    record = next((item for item in datasets if item.get("id") == dataset_id), None)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    table = record.get("table")
    if not table:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dataset table missing")
    df = load_df(table, limit=2000000)
    csv_payload = export_csv({"rows": df.to_dict(orient="records")})
    return {"kind": "dataset_csv", "payload": csv_payload}


@router.post("/datasets/chart", dependencies=[Depends(verify_auth)])
def generate_chart(payload: dict = Body(...)):
    table = payload.get("table")
    plan = payload.get("plan") or []
    if not table or not isinstance(plan, list):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing table or plan")
    df = load_df(table, limit=5000)
    summary = analyze_dataframe(df)
    charts = build_charts_from_plan(plan, df, summary)
    return {"charts": charts}
