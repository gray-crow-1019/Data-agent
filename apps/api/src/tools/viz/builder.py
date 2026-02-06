from typing import Any, Dict, List


def build_chart(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not rows:
        return {}
    labels = [row.get("segment", "all") for row in rows]
    values = [row.get("value", 0) for row in rows]
    return {
        "title": {"text": "Activation comparison"},
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": labels},
        "yAxis": {"type": "value"},
        "series": [{"type": "bar", "data": values}],
    }
