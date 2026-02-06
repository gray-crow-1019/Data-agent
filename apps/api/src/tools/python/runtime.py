from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import warnings

import pandas as pd
from sqlalchemy import text

from persistence.db import engine as app_engine


@dataclass
class DatasetSummary:
    row_count: int
    columns: List[str]
    null_rate: Dict[str, float]
    numeric_stats: Dict[str, Dict[str, float]]
    categorical_top: Dict[str, Dict[str, int]]
    numeric_std: Dict[str, float]
    column_types: Dict[str, str]
    outlier_counts: Dict[str, int]
    distinct_counts: Dict[str, int]


def analyze_dataset(table_name: str, limit: int = 5000) -> DatasetSummary:
    df = load_df(table_name, limit)
    return analyze_dataframe(df)


def build_chart(summary: DatasetSummary) -> Dict[str, Any]:
    if summary.numeric_stats:
        col = max(summary.numeric_std, key=summary.numeric_std.get)
        stats = summary.numeric_stats[col]
        return {
            "title": {"text": f"{col} 数值概览"},
            "xAxis": {"type": "category", "data": ["min", "median", "mean", "max"]},
            "yAxis": {"type": "value"},
            "series": [
                {
                    "type": "bar",
                    "data": [stats["min"], stats["median"], stats["mean"], stats["max"]],
                }
            ],
        }
    if summary.categorical_top:
        col = list(summary.categorical_top.keys())[0]
        data = summary.categorical_top[col]
        return {
            "title": {"text": f"{col} TOP 分布"},
            "xAxis": {"type": "category", "data": list(data.keys())},
            "yAxis": {"type": "value"},
            "series": [{"type": "bar", "data": list(data.values())}],
        }
    return {}


def build_analysis_bundle(
    table_name: str, limit: int = 5000
) -> Tuple[DatasetSummary, List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any], List[Dict[str, Any]]]:
    df = load_df(table_name, limit)
    summary = analyze_dataframe(df)
    raw_preview = df.head(20).fillna("").to_dict(orient="records")
    processed_preview, preprocess_plan = _preprocess_preview(raw_preview, summary)
    charts = _build_charts(summary, df)
    return summary, raw_preview, processed_preview, preprocess_plan, charts


def build_charts_from_plan(
    plan: List[Dict[str, Any]], df: pd.DataFrame, summary: DatasetSummary
) -> List[Dict[str, Any]]:
    charts: List[Dict[str, Any]] = []
    columns = set(summary.columns)
    for item in plan:
        chart_type = str(item.get("type", "")).lower()
        if "hist" in chart_type:
            chart_type = "hist"
        if "box" in chart_type:
            chart_type = "box"
        if "pie" in chart_type:
            chart_type = "pie"
        title = item.get("title") or "Chart"
        x = item.get("x")
        y = item.get("y")
        agg = item.get("agg") or "mean"
        top_n = int(item.get("top_n") or 10)
        filters = item.get("filters") or []
        filtered = _apply_filters(df, filters)
        if chart_type in {"hist", "box"}:
            target = y or x
            if not target or target not in columns:
                continue
            if chart_type == "hist":
                charts.append({**_histogram_for_numeric(target, filtered), "title": {"text": title}})
            else:
                charts.append({**_boxplot_for_numeric(target, filtered), "title": {"text": title}})
            continue
        if chart_type == "pie":
            if not x or x not in columns:
                continue
            counts = filtered[x].astype(str).value_counts().head(top_n)
            charts.append(
                {
                    "title": {"text": title},
                    "series": [{"type": "pie", "radius": "55%", "data": [{"name": k, "value": int(v)} for k, v in counts.items()]}],
                }
            )
            continue
        if chart_type == "scatter":
            if not x or not y or x not in columns or y not in columns:
                continue
            sample = filtered[[x, y]].apply(pd.to_numeric, errors="coerce").dropna().head(200)
            charts.append(
                {
                    "title": {"text": title},
                    "xAxis": {"type": "value", "name": x},
                    "yAxis": {"type": "value", "name": y},
                    "series": [{"type": "scatter", "data": sample.values.tolist()}],
                }
            )
            continue
        if chart_type in {"bar", "line"}:
            if not x or x not in columns:
                continue
            if y and y in columns:
                y_series = pd.to_numeric(filtered[y], errors="coerce")
                grouped = filtered.assign(__y=y_series).dropna(subset=["__y"]).groupby(x)["__y"]
                if agg == "sum":
                    values = grouped.sum()
                else:
                    values = grouped.mean()
            else:
                values = filtered[x].astype(str).value_counts()
            values = values.head(top_n)
            charts.append(
                {
                    "title": {"text": title},
                    "xAxis": {
                        "type": "category",
                        "data": [str(k)[:12] + "..." if len(str(k)) > 14 else str(k) for k in values.index],
                        "axisLabel": {"interval": 0, "rotate": 20},
                    },
                    "yAxis": {"type": "value"},
                    "series": [{"type": "line" if chart_type == "line" else "bar", "data": [float(v) for v in values.values]}],
                }
            )
            continue
    return [chart for chart in charts if chart.get("series")]


def _apply_filters(df: pd.DataFrame, filters: List[Dict[str, Any]]) -> pd.DataFrame:
    if not filters:
        return df
    filtered = df
    for item in filters:
        field = item.get("field")
        op = item.get("op", "eq")
        value = item.get("value")
        if field not in filtered.columns:
            continue
        series = filtered[field].astype(str)
        if op == "eq":
            filtered = filtered[series == str(value)]
        elif op == "neq":
            filtered = filtered[series != str(value)]
        elif op == "contains":
            filtered = filtered[series.str.contains(str(value), na=False)]
    return filtered


def load_df(table_name: str, limit: int) -> pd.DataFrame:
    query = f'SELECT * FROM "{table_name}" LIMIT {limit}'
    return pd.read_sql_query(text(query), app_engine)


def analyze_dataframe(df: pd.DataFrame) -> DatasetSummary:
    if df.empty:
        return DatasetSummary(
            row_count=0,
            columns=[],
            null_rate={},
            numeric_stats={},
            categorical_top={},
            numeric_std={},
            column_types={},
            outlier_counts={},
            distinct_counts={},
        )
    row_count = len(df)
    columns = list(df.columns)
    null_rate = {col: float(df[col].isna().mean()) for col in columns}
    numeric_stats: Dict[str, Dict[str, float]] = {}
    numeric_std: Dict[str, float] = {}
    categorical_top: Dict[str, Dict[str, int]] = {}
    column_types: Dict[str, str] = {}
    outlier_counts: Dict[str, int] = {}
    distinct_counts: Dict[str, int] = {}
    numeric_cols = []
    for col in columns:
        series = pd.to_numeric(df[col], errors="coerce")
        if series.notna().sum() >= max(3, row_count * 0.2):
            numeric_cols.append(col)
            numeric_stats[col] = {
                "mean": float(series.mean()),
                "median": float(series.median()),
                "min": float(series.min()),
                "max": float(series.max()),
            }
            numeric_std[col] = float(series.std()) if series.std() == series.std() else 0.0
            column_types[col] = "numeric"
            outlier_counts[col] = _count_outliers(series)
            distinct_counts[col] = int(series.nunique(dropna=True))
    for col in columns:
        if col in numeric_cols:
            continue
        if _is_datetime_like(df[col]):
            column_types[col] = "datetime"
            distinct_counts[col] = int(pd.to_datetime(df[col], errors="coerce").nunique(dropna=True))
            continue
        column_types[col] = "categorical"
        top = df[col].astype(str).value_counts().head(5)
        if not top.empty:
            categorical_top[col] = {str(k): int(v) for k, v in top.items()}
        distinct_counts[col] = int(df[col].astype(str).nunique(dropna=True))
    return DatasetSummary(
        row_count=row_count,
        columns=columns,
        null_rate=null_rate,
        numeric_stats=numeric_stats,
        categorical_top=categorical_top,
        numeric_std=numeric_std,
        column_types=column_types,
        outlier_counts=outlier_counts,
        distinct_counts=distinct_counts,
    )


def _preprocess_preview(
    raw_preview: List[Dict[str, Any]],
    summary: DatasetSummary,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    if not raw_preview:
        return [], {"steps": [], "drop_columns": [], "impute": {}, "outliers": {}}
    df = pd.DataFrame(raw_preview)
    drop_columns = [col for col, rate in summary.null_rate.items() if rate >= 0.6]
    df = df.drop(columns=drop_columns, errors="ignore")
    impute_plan: Dict[str, str] = {}
    for col, col_type in summary.column_types.items():
        if col in drop_columns or col not in df.columns:
            continue
        if col_type == "numeric":
            series = pd.to_numeric(df[col], errors="coerce")
            if series.notna().any():
                median = series.median()
                df[col] = series.fillna(median)
                impute_plan[col] = "median"
        elif col_type in ("categorical", "datetime"):
            mode = df[col].mode().iloc[0] if not df[col].mode().empty else "missing"
            df[col] = df[col].fillna(mode)
            impute_plan[col] = "mode"
    preprocess_plan = {
        "steps": [
            "删除缺失率 >= 60% 的字段",
            "数值字段使用中位数填补缺失",
            "类别/时间字段使用众数填补缺失",
            "异常值采用 IQR 标记（可选 winsorize）",
        ],
        "drop_columns": drop_columns,
        "impute": impute_plan,
        "outliers": summary.outlier_counts,
    }
    return df.fillna("").to_dict(orient="records"), preprocess_plan


def preprocess_full(df: pd.DataFrame, summary: DatasetSummary) -> pd.DataFrame:
    if df.empty:
        return df
    drop_columns = [col for col, rate in summary.null_rate.items() if rate >= 0.6]
    df = df.drop(columns=drop_columns, errors="ignore")
    for col, col_type in summary.column_types.items():
        if col in drop_columns or col not in df.columns:
            continue
        if col_type == "numeric":
            series = pd.to_numeric(df[col], errors="coerce")
            if series.notna().any():
                median = series.median()
                df[col] = series.fillna(median)
        else:
            mode = df[col].mode().iloc[0] if not df[col].mode().empty else "missing"
            df[col] = df[col].fillna(mode)
    return df


def _build_charts(summary: DatasetSummary, df: pd.DataFrame) -> List[Dict[str, Any]]:
    charts: List[Dict[str, Any]] = []
    if summary.null_rate:
        items = sorted(summary.null_rate.items(), key=lambda x: x[1], reverse=True)[:10]
        charts.append(
            {
                "title": {"text": "缺失率 Top 10"},
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": [k for k, _ in items]},
                "yAxis": {"type": "value", "axisLabel": {"formatter": "{value}%"}},
                "series": [
                    {
                        "type": "bar",
                        "data": [round(v * 100, 2) for _, v in items],
                    }
                ],
            }
        )
    if summary.numeric_stats:
        numeric_order = sorted(summary.numeric_std.items(), key=lambda x: x[1], reverse=True)
        for col, _ in numeric_order[:3]:
            stats = summary.numeric_stats[col]
            charts.append(
                {
                    "title": {"text": f"{col} 数值概览"},
                    "xAxis": {"type": "category", "data": ["min", "median", "mean", "max"]},
                    "yAxis": {"type": "value"},
                    "series": [
                        {
                            "type": "bar",
                            "data": [stats["min"], stats["median"], stats["mean"], stats["max"]],
                        }
                    ],
                }
            )
            charts.append(_boxplot_for_numeric(col, df))
            charts.append(_histogram_for_numeric(col, df))
    if summary.categorical_top:
        for col in list(summary.categorical_top.keys())[:3]:
            top = summary.categorical_top[col]
            if len(top) == 2:
                charts.append(
                    {
                        "title": {"text": f"{col} 二分类分布"},
                        "series": [
                            {
                                "type": "pie",
                                "radius": "55%",
                                "data": [{"name": k, "value": v} for k, v in top.items()],
                            }
                        ],
                    }
                )
            else:
                charts.append(
                    {
                        "title": {"text": f"{col} TOP 分布"},
                        "xAxis": {"type": "category", "data": list(top.keys())},
                        "yAxis": {"type": "value"},
                        "series": [{"type": "bar", "data": list(top.values())}],
                    }
                )
    # Time series chart if datetime + numeric present
    datetime_cols = [k for k, v in summary.column_types.items() if v == "datetime"]
    if datetime_cols and summary.numeric_stats:
        time_col = datetime_cols[0]
        num_col = max(summary.numeric_std, key=summary.numeric_std.get)
        series = pd.to_datetime(df[time_col], errors="coerce")
        numeric = pd.to_numeric(df[num_col], errors="coerce")
        ts = (
            pd.DataFrame({"time": series, "value": numeric})
            .dropna()
            .groupby("time")["value"]
            .mean()
            .sort_index()
            .head(200)
        )
        if not ts.empty:
            charts.append(
                {
                    "title": {"text": f"{num_col} 时间趋势"},
                    "xAxis": {"type": "category", "data": [t.strftime("%Y-%m-%d") for t in ts.index]},
                    "yAxis": {"type": "value"},
                    "series": [{"type": "line", "data": [float(v) for v in ts.values]}],
                }
            )
    return [chart for chart in charts if chart.get("series")]


def _histogram_for_numeric(column: str, df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {}
    series = pd.to_numeric(df[column], errors="coerce").dropna()
    if series.empty:
        return {}
    bins = 10
    counts = pd.cut(series, bins=bins, include_lowest=True)
    bucket_counts = counts.value_counts().sort_index()
    labels = [str(interval)[:12] + "..." if len(str(interval)) > 14 else str(interval) for interval in bucket_counts.index]
    data = [int(value) for value in bucket_counts.values]
    return {
        "title": {"text": f"{column} 直方图"},
        "xAxis": {"type": "category", "data": labels, "axisLabel": {"interval": 0, "rotate": 20}},
        "yAxis": {"type": "value"},
        "series": [{"type": "bar", "data": data}],
    }


def _boxplot_for_numeric(column: str, df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {}
    series = pd.to_numeric(df[column], errors="coerce").dropna()
    if series.empty:
        return {}
    q1 = series.quantile(0.25)
    q2 = series.quantile(0.5)
    q3 = series.quantile(0.75)
    return {
        "title": {"text": f"{column} 箱线图"},
        "xAxis": {"type": "category", "data": [column]},
        "yAxis": {"type": "value"},
        "series": [
            {
                "type": "boxplot",
                "data": [[float(series.min()), float(q1), float(q2), float(q3), float(series.max())]],
            }
        ],
    }


def _count_outliers(series: pd.Series) -> int:
    clean = series.dropna()
    if clean.empty:
        return 0
    q1 = clean.quantile(0.25)
    q3 = clean.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return int(((clean < lower) | (clean > upper)).sum())


def _is_datetime_like(series: pd.Series) -> bool:
    if series.dtype.kind in {"M"}:
        return True
    try:
        sample = series.dropna().astype(str).head(50)
        if sample.empty:
            return False
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
        return parsed.notna().mean() >= 0.6
    except Exception:
        return False
