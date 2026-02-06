from typing import Dict


def export_pdf(payload: Dict) -> bytes:
    _ = payload
    return b"%PDF-1.4"
