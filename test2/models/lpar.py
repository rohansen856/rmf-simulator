from dataclasses import dataclass
from typing import List

@dataclass
class LPARConfig:
    name: str
    cpu_capacity: int
    memory_gb: int
    workload_type: str
    peak_hours: List[int]
