from pathlib import Path

from llm.client import LLMClient
from llm.schemas import LLMRequest
from llm.tools import narrative_tool, report_template_tool
from llm.utils import extract_json, require_keys
from orchestrator.context import OrchestratorContext
from settings import get_settings


def run(ctx: OrchestratorContext) -> OrchestratorContext:
    settings = get_settings()
    if not ctx.findings:
        ctx.narrative = "No findings yet."
        return ctx

    if settings.llm_provider == "dashscope" and settings.dashscope_api_key:
        base_prompt_path = Path(__file__).resolve().parents[2] / "llm" / "prompts" / "system.md"
        base_prompt = base_prompt_path.read_text(encoding="utf-8")
        prompt_path = Path(__file__).resolve().parents[2] / "llm" / "prompts" / "narrator.md"
        prompt = prompt_path.read_text(encoding="utf-8")
        client = LLMClient()
        summary = "\n".join([f"- {finding.conclusion}: {finding.evidence}" for finding in ctx.findings])
        response = client.complete(
            LLMRequest(
                system_prompt=base_prompt,
                user_prompt=f"{prompt}\n\nFindings:\n{summary}\n请输出叙事 JSON。",
            ),
            tools=[narrative_tool()],
            tool_choice="auto",
            trace=ctx.llm_trace,
            trace_messages=ctx.llm_trace_messages,
            trace_label="narrate",
        )
        parsed = None
        if response.tool_outputs:
            parsed = response.tool_outputs[0]
        elif settings.llm_strict_json:
            parsed = extract_json(response.content)
        if parsed and require_keys(parsed, ["narrative", "confidence", "risks"]):
            risks = "; ".join(parsed.get("risks", []))
            ctx.narrative = f"{parsed['narrative']}（置信度：{parsed['confidence']}） 风险：{risks}"
            # structured report template
            report_prompt_path = Path(__file__).resolve().parents[2] / "llm" / "prompts" / "report_template.md"
            report_prompt = report_prompt_path.read_text(encoding="utf-8")
            report_response = client.complete(
                LLMRequest(
                    system_prompt=base_prompt,
                    user_prompt=f"{report_prompt}\n\nFindings:\n{summary}",
                ),
                tools=[report_template_tool()],
                tool_choice="auto",
                trace=ctx.llm_trace,
                trace_messages=ctx.llm_trace_messages,
                trace_label="report_template",
            )
            report_parsed = None
            if report_response.tool_outputs:
                report_parsed = report_response.tool_outputs[0]
            elif settings.llm_strict_json:
                report_parsed = extract_json(report_response.content)
            if report_parsed and require_keys(
                report_parsed, ["methods", "assumptions", "conclusions", "limitations"]
            ):
                ctx.artifacts["report_structured"] = report_parsed
            return ctx
        if not settings.llm_strict_json and response.content:
            ctx.narrative = response.content
            return ctx
    summary = "；".join([f"{finding.conclusion}" for finding in ctx.findings])
    ctx.narrative = f"分析完成：{summary}"
    return ctx
