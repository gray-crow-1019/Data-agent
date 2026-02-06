from dataclasses import dataclass
from time import perf_counter
from typing import Any, Dict, List, Optional

import httpx
from sqlalchemy import text

from persistence.db import engine as app_engine
from settings import get_settings


@dataclass
class SQLResult:
    rows: List[Dict[str, Any]]
    row_count: int
    duration_ms: int
    data_version: Optional[str] = None
    cache_hit: Optional[bool] = None


def run_sql(sql: str, engine: str) -> SQLResult:
    settings = get_settings()
    if engine == "clickhouse":
        return _run_clickhouse(sql, settings)
    return _run_sqlalchemy(sql)


def _run_sqlalchemy(sql: str) -> SQLResult:
    start = perf_counter()
    with app_engine.connect() as conn:
        result = conn.execute(text(sql))
        rows = [dict(row._mapping) for row in result]
    duration_ms = int((perf_counter() - start) * 1000)
    return SQLResult(rows=rows, row_count=len(rows), duration_ms=duration_ms, cache_hit=False)


def _run_clickhouse(sql: str, settings) -> SQLResult:
    start = perf_counter()
    query = f"{sql}\nFORMAT JSONEachRow"
    auth = None
    if settings.clickhouse_user:
        auth = (settings.clickhouse_user, settings.clickhouse_password)
    params = {"database": settings.clickhouse_database}
    rows: List[Dict[str, Any]] = []
    with httpx.Client(timeout=30) as client:
        response = client.post(settings.clickhouse_url, params=params, content=query, auth=auth)
        response.raise_for_status()
        for line in response.text.strip().splitlines():
            if not line:
                continue
            rows.append(httpx.Response(200, content=line).json())
    duration_ms = int((perf_counter() - start) * 1000)
    return SQLResult(rows=rows, row_count=len(rows), duration_ms=duration_ms, cache_hit=False)
