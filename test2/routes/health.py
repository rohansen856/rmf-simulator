from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@router.get("/ready")
async def ready():
    return {"status": "ready", "timestamp": datetime.now().isoformat()}

@router.get("/startup")
async def startup():
    return {"status": "started", "timestamp": datetime.now().isoformat()}
