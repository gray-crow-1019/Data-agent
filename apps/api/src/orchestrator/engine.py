from datetime import datetime
from time import perf_counter
from typing import Callable, List, Tuple

from orchestrator.context import OrchestratorContext
from orchestrator.states import (
    analyze,
    build_query_plan,
    clarify,
    execute_query,
    govern,
    narrate,
    package_artifact,
    quality_gate,
    resolve_metric,
)
from shared.types import RunStep, TaskResult, TaskSpec

StateFn = Callable[[OrchestratorContext], OrchestratorContext]

DEFAULT_STATES: List[Tuple[str, StateFn]] = [
    ("clarify", clarify.run),
    ("resolve_metric", resolve_metric.run),
    ("build_query_plan", build_query_plan.run),
    ("govern", govern.run),
    ("execute_query", execute_query.run),
    ("quality_gate", quality_gate.run),
    ("analyze", analyze.run),
    ("narrate", narrate.run),
    ("package_artifact", package_artifact.run),
]


def run(task_spec: TaskSpec) -> TaskResult:
    ctx = OrchestratorContext(task_spec=task_spec)
    for name, state in DEFAULT_STATES:
        ctx.state = name
        step = RunStep(name=name, status="running", started_at=datetime.utcnow())
        tick = perf_counter()
        ctx.steps.append(step)
        try:
            ctx = state(ctx)
            step.status = "completed"
            _attach_step_output(ctx, step, name)
        except Exception as exc:
            step.status = "failed"
            ctx.warnings.append(f"{name} failed: {exc}")
            raise
        finally:
            step.ended_at = datetime.utcnow()
            step.duration_ms = int((perf_counter() - tick) * 1000)
    ctx.state = "completed"
    return ctx.to_result()


def _attach_step_output(ctx: OrchestratorContext, step: RunStep, name: str) -> None:
    if not ctx.artifacts.get("step_outputs"):
        ctx.artifacts["step_outputs"] = {}
    snapshot = {}
    if name == "clarify":
        snapshot = {
            "question": ctx.clarified_question,
            "clarify": ctx.clarify_params.model_dump() if ctx.clarify_params else None,
        }
    elif name == "resolve_metric":
        snapshot = {"metrics": [m.model_dump() for m in ctx.metrics]}
    elif name == "build_query_plan":
        snapshot = {"query_plan": ctx.query_plan.model_dump() if ctx.query_plan else None}
    elif name == "govern":
        snapshot = {"warnings": ctx.warnings}
    elif name == "execute_query":
        snapshot = {
            "queries": [q.model_dump() for q in ctx.queries],
            "preview_rows": ctx.preview_rows,
        }
    elif name == "quality_gate":
        snapshot = {"quality": [q.model_dump() for q in ctx.quality]}
    elif name == "analyze":
        snapshot = {
            "findings": [f.model_dump() for f in ctx.findings],
            "charts": ctx.charts,
            "dataset_profile": ctx.dataset_profile,
            "preprocessing": ctx.preprocessing,
        }
    elif name == "narrate":
        snapshot = {
            "narrative": ctx.narrative,
            "chart_insights": ctx.chart_insights,
        }
    elif name == "package_artifact":
        snapshot = {"artifacts": list(ctx.artifacts.keys())}
    ctx.artifacts["step_outputs"][name] = snapshot
    step.output_ref = f"step_outputs.{name}"
