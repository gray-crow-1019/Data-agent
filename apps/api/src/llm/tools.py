from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ValidationError


class ClarifyToolOutput(BaseModel):
    time_range: Optional[str]
    granularity: Optional[str]
    subject: Optional[str]
    filters: Dict[str, Any]
    comparison: Optional[str]
    missing: List[str]


class SQLPlanToolOutput(BaseModel):
    sql: str
    assumptions: List[str]
    tables: List[str]


class NarrativeToolOutput(BaseModel):
    narrative: str
    confidence: str
    risks: List[str]


class ChartPlanItem(BaseModel):
    title: str
    type: str
    x: Optional[str] = None
    y: Optional[str] = None
    agg: Optional[str] = None
    top_n: Optional[int] = None
    reason: Optional[str] = None


class ChartPlanToolOutput(BaseModel):
    charts: List[ChartPlanItem]


class ChartInsightItem(BaseModel):
    title: str
    insight: str
    caveat: Optional[str] = None


class ChartInsightToolOutput(BaseModel):
    insights: List[ChartInsightItem]


class TaskTypeToolOutput(BaseModel):
    task_type: str
    reason: str


class ReportTemplateToolOutput(BaseModel):
    methods: List[str]
    assumptions: List[str]
    conclusions: List[str]
    limitations: List[str]


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: Dict[str, Any]

    def as_openai(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


def clarify_tool() -> ToolSpec:
    return ToolSpec(
        name="extract_clarify",
        description="Extract clarification parameters from the question.",
        parameters={
            "type": "object",
            "properties": {
                "time_range": {"type": ["string", "null"]},
                "granularity": {"type": ["string", "null"]},
                "subject": {"type": ["string", "null"]},
                "filters": {"type": "object"},
                "comparison": {"type": ["string", "null"]},
                "missing": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["time_range", "granularity", "subject", "filters", "comparison", "missing"],
        },
    )


def sql_plan_tool() -> ToolSpec:
    return ToolSpec(
        name="generate_sql_plan",
        description="Generate SQL plus assumptions and tables.",
        parameters={
            "type": "object",
            "properties": {
                "sql": {"type": "string"},
                "assumptions": {"type": "array", "items": {"type": "string"}},
                "tables": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["sql", "assumptions", "tables"],
        },
    )


def narrative_tool() -> ToolSpec:
    return ToolSpec(
        name="write_narrative",
        description="Write a concise narrative with confidence and risks.",
        parameters={
            "type": "object",
            "properties": {
                "narrative": {"type": "string"},
                "confidence": {"type": "string"},
                "risks": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["narrative", "confidence", "risks"],
        },
    )


def chart_plan_tool() -> ToolSpec:
    return ToolSpec(
        name="plan_charts",
        description="Plan charts based on dataset profile.",
        parameters={
            "type": "object",
            "properties": {
                "charts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "type": {"type": "string"},
                            "x": {"type": ["string", "null"]},
                            "y": {"type": ["string", "null"]},
                            "agg": {"type": ["string", "null"]},
                            "top_n": {"type": ["integer", "null"]},
                            "reason": {"type": ["string", "null"]},
                        },
                        "required": ["title", "type"],
                    },
                }
            },
            "required": ["charts"],
        },
    )


def chart_insight_tool() -> ToolSpec:
    return ToolSpec(
        name="chart_insights",
        description="Generate insights for each chart based on summary statistics.",
        parameters={
            "type": "object",
            "properties": {
                "insights": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "insight": {"type": "string"},
                            "caveat": {"type": ["string", "null"]},
                        },
                        "required": ["title", "insight"],
                    },
                }
            },
            "required": ["insights"],
        },
    )


def task_type_tool() -> ToolSpec:
    return ToolSpec(
        name="classify_task",
        description="Classify analysis task type based on question and dataset profile.",
        parameters={
            "type": "object",
            "properties": {
                "task_type": {"type": "string"},
                "reason": {"type": "string"},
            },
            "required": ["task_type", "reason"],
        },
    )


def report_template_tool() -> ToolSpec:
    return ToolSpec(
        name="report_template",
        description="Generate structured analysis report template.",
        parameters={
            "type": "object",
            "properties": {
                "methods": {"type": "array", "items": {"type": "string"}},
                "assumptions": {"type": "array", "items": {"type": "string"}},
                "conclusions": {"type": "array", "items": {"type": "string"}},
                "limitations": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["methods", "assumptions", "conclusions", "limitations"],
        },
    )


def execute_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if name == "extract_clarify":
            return ClarifyToolOutput(**arguments).model_dump()
        if name == "generate_sql_plan":
            return SQLPlanToolOutput(**arguments).model_dump()
        if name == "write_narrative":
            return NarrativeToolOutput(**arguments).model_dump()
        if name == "plan_charts":
            return ChartPlanToolOutput(**arguments).model_dump()
        if name == "chart_insights":
            return ChartInsightToolOutput(**arguments).model_dump()
        if name == "classify_task":
            return TaskTypeToolOutput(**arguments).model_dump()
        if name == "report_template":
            return ReportTemplateToolOutput(**arguments).model_dump()
    except ValidationError as exc:
        return {"error": str(exc)}
    return {"error": f"unknown tool: {name}"}
