from orchestrator.context import OrchestratorContext
from governance.guardrails import apply_guardrails
from governance.masking import mask_pii
from governance.pii import detect_pii
from governance.policy_engine import evaluate_policies
from governance.audit import record_audit
from settings import get_settings


def run(ctx: OrchestratorContext) -> OrchestratorContext:
    settings = get_settings()
    payload = {
        "task_id": ctx.task_spec.id,
        "question": ctx.task_spec.question,
        "metrics": [metric.name for metric in ctx.metrics],
        "sql": ctx.query_plan.sql if ctx.query_plan else None,
    }
    policy = evaluate_policies(payload)
    if not policy.get("allowed", True):
        ctx.warnings.append("Policy denied execution")
        return ctx
    pii = detect_pii(payload)
    if pii.get("found"):
        ctx.warnings.append("PII detected; masking applied")
        ctx.artifacts["pii_fields"] = pii.get("fields", [])
        ctx.query_results = mask_pii({"rows": ctx.query_results}).get("rows", ctx.query_results)
    ctx.artifacts["guardrails"] = apply_guardrails(payload)
    record_audit({"task_id": ctx.task_spec.id, "policy": policy})

    if not settings.allow_detail_export:
        ctx.preview_rows = []
        ctx.warnings.append("Detail export disabled by policy")
    return ctx
