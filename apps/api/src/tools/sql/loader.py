from __future__ import annotations

import os
from typing import List, Tuple

import pandas as pd
from scipy.io import loadmat
from sqlalchemy import text

from persistence.db import engine as app_engine


class DatasetLoadError(Exception):
    pass


def load_dataset_to_db(file_path: str, table_name: str) -> Tuple[List[str], int]:
    if not os.path.exists(file_path):
        raise DatasetLoadError("file not found")

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(file_path)
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    elif ext == ".mat":
        df = _load_mat_to_df(file_path)
    else:
        raise DatasetLoadError("unsupported file type")

    if df.empty:
        raise DatasetLoadError("empty dataset")

    df.columns = [sanitize_identifier(str(col)) for col in df.columns]

    columns_sql = ", ".join([f'"{col}" TEXT' for col in df.columns])
    with app_engine.begin() as conn:
        conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}"'))
        conn.execute(text(f'CREATE TABLE "{table_name}" ({columns_sql})'))
        df.astype(str).to_sql(table_name, conn, if_exists="append", index=False)

    return list(df.columns), len(df)


def _load_mat_to_df(file_path: str) -> pd.DataFrame:
    data = loadmat(file_path)
    # Pick first 2D array-like item
    for key, value in data.items():
        if key.startswith("__"):
            continue
        if hasattr(value, "shape") and len(value.shape) == 2:
            df = pd.DataFrame(value)
            df.columns = [f"col_{i}" for i in range(df.shape[1])]
            return df
    raise DatasetLoadError("no 2D array found in .mat")


def sanitize_identifier(value: str) -> str:
    cleaned = "".join([ch if ch.isalnum() or ch == "_" else "_" for ch in value.strip()])
    if not cleaned:
        return "col"
    if cleaned[0].isdigit():
        cleaned = f"col_{cleaned}"
    return cleaned
