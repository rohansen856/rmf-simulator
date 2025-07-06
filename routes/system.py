from fastapi import APIRouter
from datetime import datetime

from metrices.simulator import simulator
from utils.confiig import LPAR_CONFIGS

router = APIRouter()

@router.get("/")
async def root():
    return {
        "name": "RMF Monitor III Data Simulator",
        "version": "1.0.0",
        "sysplex": simulator.sysplex_name,
        "lpars": [lpar.name for lpar in LPAR_CONFIGS],
        "metrics_endpoint": "/metrics",
        "health_endpoint": "/health"
    }

@router.get("/system-info")
async def get_info():
    current_time = datetime.now()
    return {
        "sysplex": simulator.sysplex_name,
        "timestamp": current_time.isoformat(),
        "uptime_seconds": int((current_time - simulator.start_time).total_seconds()),
        "lpars": [
            {
                "name": l.name,
                "workload_type": l.workload_type,
                "cpu_capacity": l.cpu_capacity,
                "memory_gb": l.memory_gb,
                "peak_hours": l.peak_hours,
                "current_load_factor": round(simulator.get_time_factor(l), 2),
                "is_peak_hour": current_time.hour in l.peak_hours
            }
            for l in LPAR_CONFIGS
        ]
    }
