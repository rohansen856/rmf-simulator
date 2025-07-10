from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from storage.mongodb.service import MongoDBService
from utils.logger import logger
from storage.mysql.service import DatabaseService
from storage.S3.s3 import S3StorageService

router = APIRouter()
db = DatabaseService()
mongo = MongoDBService()
s3 = S3StorageService()

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

@router.get("/mongodb-summary")
async def mongodb_summary():
    """Get MongoDB metrics summary"""
    try:
        summary = mongo.get_metrics_summary()
        return {"summary": summary}
    except Exception as e:
        return {"error": str(e)}

@router.get("/mongodb-latest/{sysplex}")
async def get_latest_mongodb_metrics(sysplex: str, lpar: str = None, limit: int = 100):
    """Get latest metrics from MongoDB"""
    try:
        metrics = mongo.get_latest_metrics(sysplex, lpar, limit)
        return {"metrics": metrics}
    except Exception as e:
        return {"error": str(e)}

@router.get("/storage/s3/statistics")
async def get_s3_statistics():
    """Get S3 storage statistics"""
    try:
        stats = s3.get_storage_statistics()
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting S3 statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get S3 statistics: {str(e)}")

@router.get("/storage/s3/metrics/{metric_type}")
async def get_s3_metrics(
    metric_type: str,
    sysplex: Optional[str] = Query(None),
    lpar: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    limit: int = Query(100, le=10000)
):
    """Retrieve metrics from S3 storage"""
    try:
        metrics = s3.retrieve_metrics(
            metric_type=metric_type,
            sysplex=sysplex,
            lpar=lpar,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        
        return {
            "status": "success",
            "metric_type": metric_type,
            "count": len(metrics),
            "metrics": metrics,
            "filters": {
                "sysplex": sysplex,
                "lpar": lpar,
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None,
                "limit": limit
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving S3 metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve metrics: {str(e)}")

@router.post("/storage/s3/backup")
async def create_s3_backup(backup_prefix: Optional[str] = None):
    """Create a backup of all S3 data"""
    try:
        backup_key = s3.create_backup(backup_prefix)
        
        if backup_key:
            return {
                "status": "success",
                "message": "Backup created successfully",
                "backup_prefix": backup_key,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Backup creation failed")
            
    except Exception as e:
        logger.error(f"Error creating S3 backup: {e}")
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")