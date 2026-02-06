import json
from pathlib import Path

from orchestrator.context import OrchestratorContext
from persistence.datasets import latest_dataset
from shared.types import FindingCard
from tools.python.runtime import build_analysis_bundle, build_charts_from_plan, load_df
from llm.client import LLMClient
from llm.schemas import LLMRequest
from llm.tools import chart_plan_tool, chart_insight_tool, task_type_tool
from llm.utils import extract_json, require_keys
from settings import get_settings


def run(ctx: OrchestratorContext) -> OrchestratorContext:
    settings = get_settings()
    dataset = latest_dataset()
    if dataset:
        summary, raw_preview, processed_preview, preprocess_plan, charts = build_analysis_bundle(
            dataset["table"]
        )
        chart_plan: list[dict] = []
        if settings.llm_provider:
            base_prompt_path = Path(__file__).resolve().parents[2] / "llm" / "prompts" / "system.md"
            base_prompt = base_prompt_path.read_text(encoding="utf-8")
            plan_prompt_path = Path(__file__).resolve().parents[2] / "llm" / "prompts" / "chart_plan.md"
            plan_prompt = plan_prompt_path.read_text(encoding="utf-8")
            client = LLMClient()
            payload = {
                "row_count": summary.row_count,
                "columns": summary.columns,
                "column_types": summary.column_types,
                "null_rate": summary.null_rate,
                "numeric_stats": summary.numeric_stats,
                "categorical_top": summary.categorical_top,
            }
            response = client.complete(
                LLMRequest(
                    system_prompt=base_prompt,
                    user_prompt=f"{plan_prompt}\n\n数据概况 JSON:\n{json.dumps(payload, ensure_ascii=False)}",
                ),
                tools=[chart_plan_tool()],
                tool_choice="auto",
                trace=ctx.llm_trace,
                trace_messages=ctx.llm_trace_messages,
                trace_label="chart_plan",
            )
            parsed = None
            if response.tool_outputs:
                parsed = response.tool_outputs[0]
            elif settings.llm_strict_json:
                parsed = extract_json(response.content)
            if parsed and require_keys(parsed, ["charts"]):
                chart_plan = parsed.get("charts", [])

        if chart_plan:
            ctx.chart_plan = chart_plan
            df = load_df(dataset["table"], limit=5000)
            planned_charts = build_charts_from_plan(chart_plan, df, summary)
            charts = planned_charts or charts
            if settings.llm_provider:
                insight_prompt_path = Path(__file__).resolve().parents[2] / "llm" / "prompts" / "chart_insight.md"
                insight_prompt = insight_prompt_path.read_text(encoding="utf-8")
                insight_payload = {
                    "chart_plan": chart_plan,
                    "row_count": summary.row_count,
                    "null_rate": summary.null_rate,
                    "numeric_stats": summary.numeric_stats,
                    "categorical_top": summary.categorical_top,
                }
                insight_response = client.complete(
                    LLMRequest(
                        system_prompt=base_prompt,
                        user_prompt=f"{insight_prompt}\n\n数据概况 JSON:\n{json.dumps(insight_payload, ensure_ascii=False)}",
                    ),
                    tools=[chart_insight_tool()],
                    tool_choice="auto",
                    trace=ctx.llm_trace,
                    trace_messages=ctx.llm_trace_messages,
                    trace_label="chart_insights",
                )
                insight_parsed = None
                if insight_response.tool_outputs:
                    insight_parsed = insight_response.tool_outputs[0]
                elif settings.llm_strict_json:
                    insight_parsed = extract_json(insight_response.content)
                if insight_parsed and require_keys(insight_parsed, ["insights"]):
                    ctx.chart_insights = insight_parsed.get("insights", [])
        if settings.llm_provider:
            type_prompt_path = Path(__file__).resolve().parents[2] / "llm" / "prompts" / "task_type.md"
            type_prompt = type_prompt_path.read_text(encoding="utf-8")
            type_payload = {
                "question": ctx.task_spec.question,
                "column_types": summary.column_types,
                "distinct_counts": summary.distinct_counts,
                "row_count": summary.row_count,
            }
            type_response = client.complete(
                LLMRequest(
                    system_prompt=base_prompt,
                    user_prompt=f"{type_prompt}\n\n数据概况 JSON:\n{json.dumps(type_payload, ensure_ascii=False)}",
                ),
                tools=[task_type_tool()],
                tool_choice="auto",
                trace=ctx.llm_trace,
                trace_messages=ctx.llm_trace_messages,
                trace_label="task_type",
            )
            type_parsed = None
            if type_response.tool_outputs:
                type_parsed = type_response.tool_outputs[0]
            elif settings.llm_strict_json:
                type_parsed = extract_json(type_response.content)
            if type_parsed and require_keys(type_parsed, ["task_type", "reason"]):
                ctx.analysis_type = type_parsed.get("task_type")
                ctx.analysis_reason = type_parsed.get("reason")
        ctx.preview_rows = raw_preview
        ctx.raw_preview_rows = raw_preview
        ctx.processed_preview_rows = processed_preview
        ctx.preprocessing = preprocess_plan
        ctx.dataset_profile = {
            "row_count": summary.row_count,
            "columns": summary.columns,
            "null_rate": summary.null_rate,
            "numeric_stats": summary.numeric_stats,
            "categorical_top": summary.categorical_top,
            "column_types": summary.column_types,
            "outlier_counts": summary.outlier_counts,
            "distinct_counts": summary.distinct_counts,
            "table": dataset["table"],
        }
        ctx.charts = charts
        ctx.chart = charts[0] if charts else {}
        ctx.findings.append(
            FindingCard(
                conclusion=f"数据概况：{dataset['filename']}",
                evidence=f"表名 {dataset['table']}，行数 {summary.row_count}，字段数 {len(summary.columns)}。",
                confidence="high",
                alternative_explanations=[],
                next_steps=["查看缺失率与异常值摘要", "选择关注字段生成趋势或分布图"],
                detail="已完成字段统计、缺失率、异常值与分布概览。",
            )
        )
        high_missing = sorted(summary.null_rate.items(), key=lambda x: x[1], reverse=True)[:3]
        if high_missing:
            miss_text = ", ".join([f"{k}:{v:.0%}" for k, v in high_missing])
            ctx.findings.append(
                FindingCard(
                    conclusion="缺失率最高字段",
                    evidence=miss_text,
                    confidence="medium",
                    alternative_explanations=[],
                    next_steps=["考虑删除或填补缺失字段"],
                    detail="基于缺失率排序。",
                )
            )
        if summary.numeric_stats:
            col = max(summary.numeric_std, key=summary.numeric_std.get)
            stats = summary.numeric_stats[col]
            outliers = summary.outlier_counts.get(col, 0)
            ctx.findings.append(
                FindingCard(
                    conclusion=f"波动最大的数值字段：{col}",
                    evidence=(
                        f"min={stats['min']:.3f}, median={stats['median']:.3f}, "
                        f"mean={stats['mean']:.3f}, max={stats['max']:.3f}，异常值 {outliers} 条"
                    ),
                    confidence="medium",
                    alternative_explanations=[],
                    next_steps=["检查异常值", "按分组或时间维度展开"],
                    detail="按标准差排序选择字段。",
                )
            )
        if summary.categorical_top:
            col = list(summary.categorical_top.keys())[0]
            top_items = summary.categorical_top[col]
            top_text = ", ".join([f"{k}:{v}" for k, v in top_items.items()])
            ctx.findings.append(
                FindingCard(
                    conclusion=f"类别字段 {col} TOP 分布",
                    evidence=top_text,
                    confidence="medium",
                    alternative_explanations=[],
                    next_steps=["按类别拆分指标", "进一步分析长尾类别"],
                    detail="展示首个可识别类别字段。",
                )
            )
        if ctx.analysis_type:
            ctx.findings.append(
                FindingCard(
                    conclusion=f"任务类型判定：{ctx.analysis_type}",
                    evidence=ctx.analysis_reason or "基于字段类型与用户问题综合判断。",
                    confidence="medium",
                    alternative_explanations=[],
                    next_steps=[
                        "根据任务类型选择更合适的模型或统计方法",
                        "如需预测，请补充目标字段与评估指标",
                    ],
                    detail="LLM 判定的分析类型。",
                )
            )
        return ctx

    if ctx.query_results:
        ctx.findings.append(
            FindingCard(
                conclusion="Activation improved in the latest period.",
                evidence=str(ctx.query_results[0]),
                confidence="medium",
                alternative_explanations=[
                    "Seasonality effects",
                    "Traffic mix shift",
                ],
                next_steps=[
                    "Validate by channel split",
                    "Check onboarding step drop-off",
                ],
                detail="Sample insight based on placeholder data.",
            )
        )
    return ctx
