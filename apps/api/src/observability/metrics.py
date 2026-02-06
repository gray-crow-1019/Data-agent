from dataclasses import dataclass
from typing import Dict


@dataclass
class MetricPoint:
    name: str
    value: float
    labels: Dict[str, str]


def record_metric(point: MetricPoint) -> None:
    # Placeholder for StatsD/Prometheus/etc.
    _ = point
