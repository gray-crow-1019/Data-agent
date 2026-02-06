from typing import List

from semantic.store import list_metrics
from shared.types import MetricCard


def resolve_metrics(question: str) -> List[MetricCard]:
    metrics = list_metrics()
    resolved = []
    for metric in metrics:
        if metric.name.replace("_", " ") in question.lower():
            resolved.append(
                MetricCard(
                    name=metric.name,
                    definition=metric.definition,
                    granularity=metric.granularity,
                    default_filters=metric.default_filters,
                    version=metric.version,
                    available_dimensions=metric.available_dimensions,
                    owner=metric.owner,
                )
            )
    if not resolved:
        resolved = [
            MetricCard(
                name=metrics[0].name,
                definition=metrics[0].definition,
                granularity=metrics[0].granularity,
                default_filters=metrics[0].default_filters,
                version=metrics[0].version,
                available_dimensions=metrics[0].available_dimensions,
                owner=metrics[0].owner,
            )
        ]
    return resolved
