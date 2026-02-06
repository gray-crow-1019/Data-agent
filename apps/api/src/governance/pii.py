from typing import Dict


def detect_pii(payload: Dict) -> Dict:
    return {"found": False, "fields": []}
