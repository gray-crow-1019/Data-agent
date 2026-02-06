from dataclasses import dataclass
from typing import Optional


@dataclass
class CostEstimate:
    scan_cost: str
    scan_bytes: Optional[int] = None


def estimate_cost(sql: str, engine: str) -> CostEstimate:
    _ = (sql, engine)
    return CostEstimate(scan_cost="low", scan_bytes=120_000_000)
