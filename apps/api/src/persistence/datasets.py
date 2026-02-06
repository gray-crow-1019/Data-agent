from __future__ import annotations

from typing import List, Optional

_DATASETS: List[dict] = []


def add_dataset(record: dict) -> None:
    _DATASETS.append(record)


def list_datasets() -> List[dict]:
    return list(_DATASETS)


def latest_dataset() -> Optional[dict]:
    if not _DATASETS:
        return None
    return _DATASETS[-1]
