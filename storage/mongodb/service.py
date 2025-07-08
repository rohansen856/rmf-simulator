"""
Main MongoDB Service - Orchestrates all MongoDB operations
"""
from datetime import datetime
from typing import Dict, List, Optional

from .config import MongoConfig
from .connection import MongoConnectionManager
from .schema import MongoSchemaManager
from .operations import MongoOperations
from .queries import MongoQueries
from .backup import MongoBackupManager
from utils.logger import logger


class MongoDBService:
    """
    Main MongoDB service that orchestrates all database operations
    """
    
    def __init__(self, config: Optional[MongoConfig] = None):
        self.config = config or MongoConfig()
        
        # Initialize components
        self.connection_manager = MongoConnectionManager(self.config)
        self.schema_manager = MongoSchemaManager(self.connection_manager)
        self.operations = MongoOperations(self.connection_manager)
        self.queries = MongoQueries(self.connection_manager)
        self.backup_manager = MongoBackupManager(self.connection_manager)
        
        # Initialize database
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize database and collections with proper indexes"""
        try:
            self.schema_manager.initialize_schema()
            logger.info("MongoDB service initialization completed successfully")
        except Exception as e:
            logger.error(f"MongoDB service initialization failed: {e}")
            raise
    
    # Connection and status methods
    def get_connection_status(self) -> dict:
        """Get connection status and database information"""
        return self.connection_manager.get_connection_status()
    
    def close_connection(self):
        """Close the database connection"""
        self.connection_manager.close_connection()
    
    # Metric insertion methods (delegated to operations)
    def insert_cpu_metric(self, timestamp: datetime, sysplex: str, lpar: str, 
                         cpu_type: str, utilization_percent: float):
        """Insert CPU utilization metric"""
        return self.operations.insert_cpu_metric(timestamp, sysplex, lpar, cpu_type, utilization_percent)
    
    def insert_memory_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                           memory_type: str, usage_bytes: int):
        """Insert memory usage metric"""
        return self.operations.insert_memory_metric(timestamp, sysplex, lpar, memory_type, usage_bytes)
    
    def insert_ldev_utilization_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                     device_id: str, utilization_percent: float):
        """Insert LDEV utilization metric"""
        return self.operations.insert_ldev_utilization_metric(timestamp, sysplex, lpar, device_id, utilization_percent)
    
    def insert_ldev_response_time_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                       device_type: str, response_time_seconds: float):
        """Insert LDEV response time metric"""
        return self.operations.insert_ldev_response_time_metric(timestamp, sysplex, lpar, device_type, response_time_seconds)
    
    def insert_clpr_service_time_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                      cf_link: str, service_time_microseconds: float):
        """Insert CLPR service time metric"""
        return self.operations.insert_clpr_service_time_metric(timestamp, sysplex, lpar, cf_link, service_time_microseconds)
    
    def insert_clpr_request_rate_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                      cf_link: str, request_type: str, request_rate: float):
        """Insert CLPR request rate metric"""
        return self.operations.insert_clpr_request_rate_metric(timestamp, sysplex, lpar, cf_link, request_type, request_rate)
    
    def insert_mpb_processing_rate_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                        queue_type: str, processing_rate: float):
        """Insert MPB processing rate metric"""
        return self.operations.insert_mpb_processing_rate_metric(timestamp, sysplex, lpar, queue_type, processing_rate)
    
    def insert_mpb_queue_depth_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                    queue_type: str, queue_depth: int):
        """Insert MPB queue depth metric"""
        return self.operations.insert_mpb_queue_depth_metric(timestamp, sysplex, lpar, queue_type, queue_depth)
    
    def insert_ports_utilization_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                       port_type: str, port_id: str, utilization_percent: float):
        """Insert ports utilization metric"""
        return self.operations.insert_ports_utilization_metric(timestamp, sysplex, lpar, port_type, port_id, utilization_percent)
    
    def insert_ports_throughput_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                     port_type: str, port_id: str, throughput_mbps: float):
        """Insert ports throughput metric"""
        return self.operations.insert_ports_throughput_metric(timestamp, sysplex, lpar, port_type, port_id, throughput_mbps)
    
    def insert_volumes_utilization_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                        volume_type: str, volume_id: str, utilization_percent: float):
        """Insert volumes utilization metric"""
        return self.operations.insert_volumes_utilization_metric(timestamp, sysplex, lpar, volume_type, volume_id, utilization_percent)
    
    def insert_volumes_iops_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                 volume_type: str, volume_id: str, iops: int):
        """Insert volumes IOPS metric"""
        return self.operations.insert_volumes_iops_metric(timestamp, sysplex, lpar, volume_type, volume_id, iops)
    
    # Bulk operations
    def bulk_insert_metrics(self, collection_name: str, documents: List[Dict]):
        """Bulk insert multiple documents for better performance"""
        return self.operations.bulk_insert_metrics(collection_name, documents)
    
    # Query methods (delegated to queries)
    def get_metrics_summary(self, start_time: datetime = None, end_time: datetime = None) -> Dict:
        """Get a summary of metrics for a time range"""
        return self.queries.get_metrics_summary(start_time, end_time)
    
    def get_latest_metrics(self, sysplex: str = None, lpar: str = None, 
                          limit: int = 100) -> Dict[str, List[Dict]]:
        """Get latest metrics for a specific sysplex/lpar"""
        return self.queries.get_latest_metrics(sysplex, lpar, limit)
    
    def get_metrics_aggregation(self, collection_name: str, pipeline: List[Dict]) -> List[Dict]:
        """Run aggregation pipeline on specified collection"""
        return self.queries.get_metrics_aggregation(collection_name, pipeline)
    
    def get_cpu_metrics_by_time_range(self, start_time: datetime, end_time: datetime,
                                     sysplex: str = None, lpar: str = None) -> List[Dict]:
        """Get CPU metrics within a specific time range"""
        return self.queries.get_cpu_metrics_by_time_range(start_time, end_time, sysplex, lpar)
    
    def get_memory_metrics_by_time_range(self, start_time: datetime, end_time: datetime,
                                        sysplex: str = None, lpar: str = None) -> List[Dict]:
        """Get memory metrics within a specific time range"""
        return self.queries.get_memory_metrics_by_time_range(start_time, end_time, sysplex, lpar)
    
    def get_average_utilization_by_lpar(self, collection_name: str,
                                       start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get average utilization grouped by LPAR"""
        return self.queries.get_average_utilization_by_lpar(collection_name, start_time, end_time)
    
    def get_peak_utilization_periods(self, collection_name: str, threshold: float,
                                   start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get periods where utilization exceeded threshold"""
        return self.queries.get_peak_utilization_periods(collection_name, threshold, start_time, end_time)
    
    # Data management methods
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data beyond retention period"""
        return self.operations.cleanup_old_data(days_to_keep)
    
    # Backup methods (delegated to backup manager)
    def create_backup(self, backup_path: str = None) -> Optional[str]:
        """Create a backup of the database"""
        return self.backup_manager.create_backup(backup_path)
    
    def restore_backup(self, backup_path: str, drop_existing: bool = False) -> bool:
        """Restore database from backup"""
        return self.backup_manager.restore_backup(backup_path, drop_existing)
    
    def export_collection_to_json(self, collection_name: str, output_path: str,
                                 query_filter: dict = None) -> bool:
        """Export a collection to JSON file"""
        return self.backup_manager.export_collection_to_json(collection_name, output_path, query_filter)
    
    def import_collection_from_json(self, collection_name: str, input_path: str,
                                   drop_existing: bool = False) -> bool:
        """Import a collection from JSON file"""
        return self.backup_manager.import_collection_from_json(collection_name, input_path, drop_existing)


# Factory function for easy service creation
def create_mongo_service(config: Optional[MongoConfig] = None) -> MongoDBService:
    """Factory function to create and initialize MongoDB service"""
    return MongoDBService(config)