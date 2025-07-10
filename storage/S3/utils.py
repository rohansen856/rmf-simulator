from datetime import datetime
from typing import Any, Dict
from storage.S3.s3 import S3StorageService
from storage.mongodb.service import MongoDBService
from storage.mysql.service import DatabaseService
from utils.logger import logger

def _initialize_storage_services(self, enable_mysql: bool, enable_mongodb: bool, enable_s3: bool):
    """Initialize storage services based on configuration"""
    try:
        if enable_mysql:
            self.db_service = DatabaseService()
            logger.info("MySQL storage service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize MySQL service: {e}")
        self.db_service = None
    
    try:
        if enable_mongodb:
            self.mongo_service = MongoDBService()
            logger.info("MongoDB storage service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB service: {e}")
        self.mongo_service = None
    
    try:
        if enable_s3:
            self.s3_service = S3StorageService()
            logger.info("S3 storage service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize S3 service: {e}")
        self.s3_service = None

def get_storage_status(self) -> Dict[str, Any]:
        """Get status of all storage systems"""
        status = {
            'mysql': {'enabled': self.db_service is not None},
            'mongodb': {'enabled': self.mongo_service is not None},
            's3': {'enabled': self.s3_service is not None}
        }
        
        # Get detailed status for each enabled service
        if self.db_service:
            try:
                mysql_status = self.db_service.get_connection_status()
                status['mysql'].update(mysql_status)
            except Exception as e:
                status['mysql']['error'] = str(e)
        
        if self.mongo_service:
            try:
                mongo_status = self.mongo_service.get_connection_status()
                status['mongodb'].update(mongo_status)
            except Exception as e:
                status['mongodb']['error'] = str(e)
        
        if self.s3_service:
            try:
                s3_status = self.s3_service.get_connection_status()
                s3_stats = self.s3_service.get_storage_statistics()
                status['s3'].update(s3_status)
                status['s3']['statistics'] = s3_stats
                status['s3']['batch_buffer_size'] = len(self.s3_batch_buffer)
            except Exception as e:
                status['s3']['error'] = str(e)
        
        return status
    
def export_s3_data_to_csv(self, metric_type: str, output_path: str = None,
                            sysplex: str = None, lpar: str = None,
                            start_time: datetime = None, end_time: datetime = None) -> str:
    """Export S3 data to CSV"""
    if not self.s3_service:
        logger.error("S3 service not available for export")
        return None
    
    try:
        return self.s3_service.export_metrics_to_csv(
            metric_type=metric_type,
            output_path=output_path,
            sysplex=sysplex,
            lpar=lpar,
            start_time=start_time,
            end_time=end_time
        )
    except Exception as e:
        logger.error(f"Error exporting S3 data to CSV: {e}")
        return None
    
def create_data_archive(self, start_date: datetime, end_date: datetime) -> str:
    """Create archive of historical data"""
    if not self.s3_service:
        logger.error("S3 service not available for archiving")
        return None
    
    try:
        return self.s3_service.create_archive(start_date, end_date)
    except Exception as e:
        logger.error(f"Error creating data archive: {e}")
        return None
    
def cleanup_old_data(self, days_to_keep: int = 90):
    """Clean up old data from all storage systems"""
    cleanup_results = {}
    
    # MySQL cleanup
    if self.db_service:
        try:
            mysql_deleted = self.db_service.cleanup_old_data(days_to_keep)
            cleanup_results['mysql'] = {'deleted_records': mysql_deleted}
        except Exception as e:
            cleanup_results['mysql'] = {'error': str(e)}
    
    # MongoDB cleanup
    if self.mongo_service:
        try:
            mongo_deleted = self.mongo_service.cleanup_old_data(days_to_keep)
            cleanup_results['mongodb'] = {'deleted_records': mongo_deleted}
        except Exception as e:
            cleanup_results['mongodb'] = {'error': str(e)}
    
    # S3 cleanup
    if self.s3_service:
        try:
            self.s3_service.cleanup_old_data(days_to_keep)
            cleanup_results['s3'] = {'status': 'completed'}
        except Exception as e:
            cleanup_results['s3'] = {'error': str(e)}
    
    return cleanup_results
    
def close_all_connections(self):
    """Close all storage connections"""
    try:
        # Flush any remaining S3 batch data
        self._flush_s3_batch()
        
        if self.db_service:
            self.db_service.close_connection()
        
        if self.mongo_service:
            self.mongo_service.close_connection()
        
        if self.s3_service:
            self.s3_service.close_connection()
        
        logger.info("All storage connections closed")
        
    except Exception as e:
        logger.error(f"Error closing storage connections: {e}")