from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from shared.types import (
    ClarifyParams,
    FindingCard,
    MetricCard,
    QueryCard,
    QueryPlan,
    QualityCard,
    RunStep,
    TaskResult,
    TaskSpec,
)


@dataclass
class OrchestratorContext:
    task_spec: TaskSpec
    clarified_question: Optional[str] = None
    clarify_params: Optional[ClarifyParams] = None
    state: Optional[str] = None
    steps: List[RunStep] = field(default_factory=list)
    metrics: List[MetricCard] = field(default_factory=list)
    query_plan: Optional[QueryPlan] = None
    queries: List[QueryCard] = field(default_factory=list)
    query_results: List[Dict[str, Any]] = field(default_factory=list)
    quality: List[QualityCard] = field(default_factory=list)
    findings: List[FindingCard] = field(default_factory=list)
    narrative: Optional[str] = None
    chart: Dict[str, Any] = field(default_factory=dict)
    charts: List[Dict[str, Any]] = field(default_factory=list)
    chart_plan: List[Dict[str, Any]] = field(default_factory=list)
    chart_insights: List[Dict[str, Any]] = field(default_factory=list)
    analysis_type: Optional[str] = None
    analysis_reason: Optional[str] = None
    preview_rows: List[Dict[str, Any]] = field(default_factory=list)
    raw_preview_rows: List[Dict[str, Any]] = field(default_factory=list)
    processed_preview_rows: List[Dict[str, Any]] = field(default_factory=list)
    preprocessing: Dict[str, Any] = field(default_factory=dict)
    dataset_profile: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    llm_trace: List[Dict[str, Any]] = field(default_factory=list)
    llm_trace_messages: List[Dict[str, Any]] = field(default_factory=list)

    def to_result(self) -> TaskResult:
        return TaskResult(
            task_id=self.task_spec.id,
            status="completed",
            state=self.state,
            steps=self.steps,
            clarify=self.clarify_params,
            metrics=self.metrics,
            queries=self.queries,
            quality=self.quality,
            findings=self.findings,
            narrative=self.narrative,
            chart=self.chart,
            charts=self.charts,
            chart_plan=self.chart_plan,
            chart_insights=self.chart_insights,
            analysis_type=self.analysis_type,
            analysis_reason=self.analysis_reason,
            preview_rows=self.preview_rows,
            raw_preview_rows=self.raw_preview_rows,
            processed_preview_rows=self.processed_preview_rows,
            preprocessing=self.preprocessing,
            dataset_profile=self.dataset_profile,
            warnings=self.warnings,
            artifacts={
                **self.artifacts,
                "llm_trace": self.llm_trace,
                "llm_trace_messages": self.llm_trace_messages,
            },
        )
