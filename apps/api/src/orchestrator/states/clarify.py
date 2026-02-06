from pathlib import Path

from llm.client import LLMClient
from llm.schemas import LLMRequest
from llm.tools import clarify_tool
from llm.utils import extract_json, require_keys
from orchestrator.context import OrchestratorContext
from settings import get_settings
from shared.types import ClarifyParams


def run(ctx: OrchestratorContext) -> OrchestratorContext:
    question = ctx.task_spec.question.strip()
    ctx.clarified_question = question
    settings = get_settings()
    missing = []
    time_range = None
    granularity = None
    comparison = None
    lowered = question.lower()
    if any(token in lowered for token in ["last", "week", "month", "q", "yoy", "mom"]):
        time_range = "auto"
    else:
        missing.append("time_range")
    if any(token in lowered for token in ["daily", "weekly", "monthly", "q"]):
        granularity = "auto"
    else:
        missing.append("granularity")
    if any(token in lowered for token in ["vs", "versus", "compare", "comparison"]):
        comparison = "auto"
    clarify = ClarifyParams(
        time_range=time_range,
        granularity=granularity,
        subject="metric",
        filters={},
        comparison=comparison,
        missing=missing,
    )

    if settings.llm_provider:
        base_prompt_path = Path(__file__).resolve().parents[2] / "llm" / "prompts" / "system.md"
        base_prompt = base_prompt_path.read_text(encoding="utf-8")
        prompt_path = Path(__file__).resolve().parents[2] / "llm" / "prompts" / "clarify.md"
        prompt = prompt_path.read_text(encoding="utf-8")
        client = LLMClient()
        response = client.complete(
            LLMRequest(
                system_prompt=base_prompt,
                user_prompt=(
                    f"{prompt}\n\n问题：{question}\n请输出对应 JSON。"
                ),
            ),
            tools=[clarify_tool()],
            tool_choice="auto",
            trace=ctx.llm_trace,
            trace_messages=ctx.llm_trace_messages,
            trace_label="clarify",
        )
        parsed = None
        if response.tool_outputs:
            parsed = response.tool_outputs[0]
        elif settings.llm_strict_json:
            parsed = extract_json(response.content)
        if parsed and require_keys(
            parsed, ["time_range", "granularity", "subject", "filters", "comparison", "missing"]
        ):
            clarify = ClarifyParams(**parsed)

    ctx.clarify_params = clarify
    if clarify.missing:
        ctx.warnings.append(f"Clarification needed: {', '.join(clarify.missing)}")
    return ctx
