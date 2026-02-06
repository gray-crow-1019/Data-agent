from typing import Dict, List


def export_csv(payload: Dict) -> str:
    rows: List[Dict] = payload.get("rows", [])
    if not rows:
        return ""
    headers = list(rows[0].keys())
    lines = [",".join(headers)]
    for row in rows:
        lines.append(",".join(str(row.get(h, "")) for h in headers))
    return "\n".join(lines) + "\n"
