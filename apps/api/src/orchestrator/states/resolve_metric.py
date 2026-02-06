from orchestrator.context import OrchestratorContext
from semantic.resolver import resolve_metrics


def run(ctx: OrchestratorContext) -> OrchestratorContext:
    ctx.metrics = resolve_metrics(ctx.clarified_question or ctx.task_spec.question)
    return ctx
