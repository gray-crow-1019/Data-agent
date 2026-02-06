from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TaskSpec(BaseModel):
    id: str
    question: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "running"
    meta: Dict[str, Any] = Field(default_factory=dict)
    labels: List[str] = Field(default_factory=list)


class ClarifyParams(BaseModel):
    time_range: Optional[str] = None
    granularity: Optional[str] = None
    subject: Optional[str] = None
    filters: Dict[str, Any] = Field(default_factory=dict)
    comparison: Optional[str] = None
    missing: List[str] = Field(default_factory=list)


class RunStep(BaseModel):
    name: str
    status: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    summary: Optional[str] = None
    output_ref: Optional[str] = None


class MetricCard(BaseModel):
    name: str
    definition: str
    granularity: Optional[str] = None
    default_filters: Dict[str, Any] = Field(default_factory=dict)
    version: Optional[str] = None
    available_dimensions: List[str] = Field(default_factory=list)
    owner: Optional[str] = None
    status: str = "draft"


class QueryCard(BaseModel):
    title: str
    sql: str
    engine: str
    params: Dict[str, Any] = Field(default_factory=dict)
    scan_cost: Optional[str] = None
    row_count: Optional[int] = None
    duration_ms: Optional[int] = None
    data_version: Optional[str] = None
    cache_hit: Optional[bool] = None
    estimated_cost: Optional[str] = None
    notes: Optional[str] = None


class QualityCard(BaseModel):
    check: str
    passed: bool
    reason: Optional[str] = None
    freshness_hours: Optional[float] = None
    missing_rate: Optional[float] = None
    anomaly_score: Optional[float] = None
    drift_score: Optional[float] = None
    constraints: Dict[str, Any] = Field(default_factory=dict)


class FindingCard(BaseModel):
    conclusion: str
    evidence: str
    confidence: str = "medium"
    alternative_explanations: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    detail: Optional[str] = None


class QueryPlan(BaseModel):
    engine: str
    sql: str
    assumptions: List[str] = Field(default_factory=list)
    params: Dict[str, Any] = Field(default_factory=dict)
    tables: List[str] = Field(default_factory=list)


class TaskResult(BaseModel):
    task_id: str
    status: str
    state: Optional[str] = None
    steps: List[RunStep] = Field(default_factory=list)
    clarify: Optional[ClarifyParams] = None
    metrics: List[MetricCard] = Field(default_factory=list)
    queries: List[QueryCard] = Field(default_factory=list)
    quality: List[QualityCard] = Field(default_factory=list)
    findings: List[FindingCard] = Field(default_factory=list)
    narrative: Optional[str] = None
    chart: Dict[str, Any] = Field(default_factory=dict)
    charts: List[Dict[str, Any]] = Field(default_factory=list)
    chart_plan: List[Dict[str, Any]] = Field(default_factory=list)
    chart_insights: List[Dict[str, Any]] = Field(default_factory=list)
    analysis_type: Optional[str] = None
    analysis_reason: Optional[str] = None
    preview_rows: List[Dict[str, Any]] = Field(default_factory=list)
    raw_preview_rows: List[Dict[str, Any]] = Field(default_factory=list)
    processed_preview_rows: List[Dict[str, Any]] = Field(default_factory=list)
    preprocessing: Dict[str, Any] = Field(default_factory=dict)
    dataset_profile: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    artifacts: Dict[str, Any] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    spec: TaskSpec
    result: Optional[TaskResult] = None
