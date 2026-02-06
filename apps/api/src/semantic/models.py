from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Metric:
    name: str
    definition: str
    granularity: Optional[str] = None
    default_filters: Dict[str, str] = field(default_factory=dict)
    version: Optional[str] = None
    available_dimensions: List[str] = field(default_factory=list)
    owner: Optional[str] = None


@dataclass
class Dimension:
    name: str
    description: str
    hierarchy: Optional[str] = None
    primary_key: Optional[str] = None
    joinable_to: List[str] = field(default_factory=list)
