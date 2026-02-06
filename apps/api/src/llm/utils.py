from __future__ import annotations

import json
from typing import Any, Optional


def extract_json(text: str) -> Optional[dict[str, Any]]:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    snippet = text[start : end + 1]
    try:
        return json.loads(snippet)
    except json.JSONDecodeError:
        return None


def require_keys(payload: dict[str, Any], keys: list[str]) -> bool:
    return all(key in payload for key in keys)
