import json

from orchestrator.context import OrchestratorContext
from tools.export.dataset_csv import export_csv
from tools.export.report_md import export_markdown


def run(ctx: OrchestratorContext) -> OrchestratorContext:
    ctx.artifacts["report_md"] = export_markdown(
        {
            "findings": ctx.findings,
            "dataset_profile": ctx.dataset_profile,
            "preprocessing": ctx.preprocessing,
            "chart_insights": ctx.chart_insights,
        }
    )
    ctx.artifacts["dataset_csv"] = export_csv({"rows": ctx.preview_rows})
    ctx.artifacts["processed_csv"] = export_csv({"rows": ctx.processed_preview_rows})
    ctx.artifacts["charts_json"] = json.dumps(ctx.charts, ensure_ascii=False)
    return ctx
