from enum import Enum

class MetricType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    LDEV = "ldev"
    CLPR = "clpr"
    MPB = "mpb"
    PORTS = "ports"
    VOLUMES = "volumes"
