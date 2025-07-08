from datetime import datetime
from fastapi import APIRouter
from utils.logger import logger
from storage.mysql.service import DatabaseService

router = APIRouter()
db = DatabaseService()

@router.get("/database-summary")
async def get_database_summary():
    """Get database metrics summary"""
    try:
        summary = db.get_metrics_summary()
        return {
            "database_status": "connected",
            "metrics_summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting database summary: {e}")
        return {
            "database_status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/cleanup-old-data")
async def cleanup_old_data(days_to_keep: int = 90):
    """Clean up old data beyond retention period"""
    try:
        db.cleanup_old_data(days_to_keep)
        return {
            "status": "success",
            "message": f"Cleaned up data older than {days_to_keep} days",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error cleaning up old data: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }