from typing import Dict, List


def export_markdown(payload: Dict) -> str:
    findings: List = payload.get("findings", [])
    profile = payload.get("dataset_profile", {}) or {}
    preprocessing = payload.get("preprocessing", {}) or {}

    lines = ["# Analysis Report", ""]
    if profile:
        lines.append("## Dataset Profile")
        lines.append(f"- Rows: {profile.get('row_count', 'n/a')}")
        lines.append(f"- Columns: {len(profile.get('columns', []))}")
        lines.append("")
    if preprocessing:
        lines.append("## Preprocessing Plan")
        for step in preprocessing.get("steps", []):
            lines.append(f"- {step}")
        drops = preprocessing.get("drop_columns", [])
        if drops:
            lines.append(f"- Drop columns: {', '.join(drops)}")
        lines.append("")
    chart_insights = payload.get("chart_insights", [])
    if chart_insights:
        lines.append("## Chart Insights")
        for item in chart_insights:
            title = item.get("title", "Chart")
            insight = item.get("insight", "")
            caveat = item.get("caveat", "")
            lines.append(f"- {title}: {insight}")
            if caveat:
                lines.append(f"  - Caveat: {caveat}")
        lines.append("")
    lines.append("## Findings")
    if not findings:
        lines.append("- No findings.")
    else:
        for finding in findings:
            headline = getattr(finding, "conclusion", "Finding")
            evidence = getattr(finding, "evidence", "")
            detail = getattr(finding, "detail", None)
            steps = getattr(finding, "next_steps", None)
            lines.append(f"- {headline}")
            if evidence:
                lines.append(f"  - Evidence: {evidence}")
            if detail:
                lines.append(f"  - Detail: {detail}")
            if steps:
                lines.append(f"  - Next steps: {', '.join(steps)}")
    return "\n".join(lines) + "\n"
