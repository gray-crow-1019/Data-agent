from orchestrator.context import OrchestratorContext
from settings import get_settings
from shared.types import QualityCard


def run(ctx: OrchestratorContext) -> OrchestratorContext:
    settings = get_settings()
    passed = bool(ctx.query_results)
    small_sample = len(ctx.query_results) < settings.min_group_size
    if small_sample:
        ctx.warnings.append("Sample below minimum group size. Aggregated view only.")
        ctx.preview_rows = []
    ctx.quality.append(
        QualityCard(
            check="non_empty_result",
            passed=passed,
            reason="No rows returned" if not passed else None,
            freshness_hours=2.0,
            missing_rate=0.0,
            anomaly_score=0.1,
            drift_score=0.05,
            constraints={"min_group_size": settings.min_group_size},
        )
    )
    return ctx
