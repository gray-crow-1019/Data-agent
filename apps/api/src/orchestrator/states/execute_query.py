from orchestrator.context import OrchestratorContext
from settings import get_settings
from tools.sql.runner import run_sql
from tools.viz.builder import build_chart


def run(ctx: OrchestratorContext) -> OrchestratorContext:
    if ctx.query_plan:
        settings = get_settings()
        try:
            result = run_sql(ctx.query_plan.sql, ctx.query_plan.engine)
            ctx.query_results = result.rows
            ctx.preview_rows = result.rows[: settings.data_preview_limit]
        except Exception as exc:
            ctx.warnings.append(f"SQL execution failed: {exc}")
            ctx.query_results = []
            ctx.preview_rows = []
            return ctx
        if ctx.queries:
            ctx.queries[-1].row_count = result.row_count
            ctx.queries[-1].duration_ms = result.duration_ms
            ctx.queries[-1].data_version = result.data_version
            ctx.queries[-1].cache_hit = result.cache_hit
        ctx.chart = build_chart(result.rows)
    return ctx
