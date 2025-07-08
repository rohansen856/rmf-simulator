from datetime import datetime
from typing import Dict, List, Optional, Any
from utils.logger import logger
from .config import DatabaseConfig
from .initializer import DatabaseInitializer
from .metrics_dao import MetricsDAO
from .query_dao import QueryDAO
from .maintenance_dao import MaintenanceDAO

class DatabaseService:
    """Main database service that orchestrates all database operations"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        
        # Initialize components
        self.initializer = DatabaseInitializer(self.config)
        self.metrics_dao = MetricsDAO(self.config)
        self.query_dao = QueryDAO(self.config)
        self.maintenance_dao = MaintenanceDAO(self.config)
        
        # Initialize database on startup
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize database, user, and tables if they don't exist"""
        try:
            self.initializer.initialize_database()
            logger.info("Database service initialized successfully")
        except Exception as e:
            logger.error(f"Database service initialization failed: {e}")
            raise
    
    # Metrics insertion methods (delegate to MetricsDAO)
    def insert_cpu_metric(self, timestamp: datetime, sysplex: str, lpar: str, 
                         cpu_type: str, utilization_percent: float):
        """Insert CPU utilization metric"""
        return self.metrics_dao.insert_cpu_metric(timestamp, sysplex, lpar, cpu_type, utilization_percent)
    
    def insert_memory_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                           memory_type: str, usage_bytes: int):
        """Insert memory usage metric"""
        return self.metrics_dao.insert_memory_metric(timestamp, sysplex, lpar, memory_type, usage_bytes)
    
    def insert_ldev_utilization_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                     device_id: str, utilization_percent: float):
        """Insert LDEV utilization metric"""
        return self.metrics_dao.insert_ldev_utilization_metric(timestamp, sysplex, lpar, device_id, utilization_percent)
    
    def insert_ldev_response_time_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                       device_type: str, response_time_seconds: float):
        """Insert LDEV response time metric"""
        return self.metrics_dao.insert_ldev_response_time_metric(timestamp, sysplex, lpar, device_type, response_time_seconds)
    
    def insert_clpr_service_time_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                      cf_link: str, service_time_microseconds: float):
        """Insert CLPR service time metric"""
        return self.metrics_dao.insert_clpr_service_time_metric(timestamp, sysplex, lpar, cf_link, service_time_microseconds)
    
    def insert_clpr_request_rate_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                      cf_link: str, request_type: str, request_rate: float):
        """Insert CLPR request rate metric"""
        return self.metrics_dao.insert_clpr_request_rate_metric(timestamp, sysplex, lpar, cf_link, request_type, request_rate)
    
    def insert_mpb_processing_rate_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                        queue_type: str, processing_rate: float):
        """Insert MPB processing rate metric"""
        return self.metrics_dao.insert_mpb_processing_rate_metric(timestamp, sysplex, lpar, queue_type, processing_rate)
    
    def insert_mpb_queue_depth_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                    queue_type: str, queue_depth: int):
        """Insert MPB queue depth metric"""
        return self.metrics_dao.insert_mpb_queue_depth_metric(timestamp, sysplex, lpar, queue_type, queue_depth)
    
    def insert_ports_utilization_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                       port_type: str, port_id: str, utilization_percent: float):
        """Insert ports utilization metric"""
        return self.metrics_dao.insert_ports_utilization_metric(timestamp, sysplex, lpar, port_type, port_id, utilization_percent)
    
    def insert_ports_throughput_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                     port_type: str, port_id: str, throughput_mbps: float):
        """Insert ports throughput metric"""
        return self.metrics_dao.insert_ports_throughput_metric(timestamp, sysplex, lpar, port_type, port_id, throughput_mbps)
    
    def insert_volumes_utilization_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                        volume_type: str, volume_id: str, utilization_percent: float):
        """Insert volumes utilization metric"""
        return self.metrics_dao.insert_volumes_utilization_metric(timestamp, sysplex, lpar, volume_type, volume_id, utilization_percent)
    
    def insert_volumes_iops_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                 volume_type: str, volume_id: str, iops: int):
        """Insert volumes IOPS metric"""
        return self.metrics_dao.insert_volumes_iops_metric(timestamp, sysplex, lpar, volume_type, volume_id, iops)
    
    # Query methods (delegate to QueryDAO)
    def get_metrics_summary(self, start_time: datetime = None, end_time: datetime = None) -> Dict:
        """Get a summary of metrics for a time range"""
        return self.query_dao.get_metrics_summary(start_time, end_time)
    
    def get_cpu_metrics(self, start_time: datetime = None, end_time: datetime = None,
                       sysplex: str = None, lpar: str = None) -> List[Dict]:
        """Get CPU metrics with optional filters"""
        return self.query_dao.get_cpu_metrics(start_time, end_time, sysplex, lpar)
    
    def get_memory_metrics(self, start_time: datetime = None, end_time: datetime = None,
                          sysplex: str = None, lpar: str = None) -> List[Dict]:
        """Get memory metrics with optional filters"""
        return self.query_dao.get_memory_metrics(start_time, end_time, sysplex, lpar)
    
    def get_ldev_utilization_metrics(self, start_time: datetime = None, end_time: datetime = None,
                                   sysplex: str = None, lpar: str = None, device_id: str = None) -> List[Dict]:
        """Get LDEV utilization metrics with optional filters"""
        return self.query_dao.get_ldev_utilization_metrics(start_time, end_time, sysplex, lpar, device_id)
    
    def get_average_cpu_utilization(self, start_time: datetime, end_time: datetime,
                                   sysplex: str = None, lpar: str = None) -> Dict:
        """Get average CPU utilization for a time range"""
        return self.query_dao.get_average_cpu_utilization(start_time, end_time, sysplex, lpar)
    
    def get_peak_memory_usage(self, start_time: datetime, end_time: datetime,
                             sysplex: str = None, lpar: str = None) -> Dict:
        """Get peak memory usage for a time range"""
        return self.query_dao.get_peak_memory_usage(start_time, end_time, sysplex, lpar)
    
    def get_system_health_summary(self, start_time: datetime, end_time: datetime) -> Dict:
        """Get comprehensive system health summary"""
        return self.query_dao.get_system_health_summary(start_time, end_time)
    
    def get_ldev_response_time_metrics(self, start_time: datetime = None, end_time: datetime = None,
                                     sysplex: str = None, lpar: str = None, device_type: str = None) -> List[Dict]:
        """Get LDEV response time metrics with optional filters"""
        return self.query_dao.get_ldev_response_time_metrics(start_time, end_time, sysplex, lpar, device_type)
    
    def get_clpr_service_time_metrics(self, start_time: datetime = None, end_time: datetime = None,
                                    sysplex: str = None, lpar: str = None, cf_link: str = None) -> List[Dict]:
        """Get CLPR service time metrics with optional filters"""
        return self.query_dao.get_clpr_service_time_metrics(start_time, end_time, sysplex, lpar, cf_link)
    
    def get_clpr_request_rate_metrics(self, start_time: datetime = None, end_time: datetime = None,
                                    sysplex: str = None, lpar: str = None, cf_link: str = None,
                                    request_type: str = None) -> List[Dict]:
        """Get CLPR request rate metrics with optional filters"""
        return self.query_dao.get_clpr_request_rate_metrics(start_time, end_time, sysplex, lpar, cf_link, request_type)
    
    def get_mpb_processing_rate_metrics(self, start_time: datetime = None, end_time: datetime = None,
                                      sysplex: str = None, lpar: str = None, queue_type: str = None) -> List[Dict]:
        """Get MPB processing rate metrics with optional filters"""
        return self.query_dao.get_mpb_processing_rate_metrics(start_time, end_time, sysplex, lpar, queue_type)
    
    def get_mpb_queue_depth_metrics(self, start_time: datetime = None, end_time: datetime = None,
                                  sysplex: str = None, lpar: str = None, queue_type: str = None) -> List[Dict]:
        """Get MPB queue depth metrics with optional filters"""
        return self.query_dao.get_mpb_queue_depth_metrics(start_time, end_time, sysplex, lpar, queue_type)
    
    def get_ports_utilization_metrics(self, start_time: datetime = None, end_time: datetime = None,
                                    sysplex: str = None, lpar: str = None, port_type: str = None,
                                    port_id: str = None) -> List[Dict]:
        """Get ports utilization metrics with optional filters"""
        return self.query_dao.get_ports_utilization_metrics(start_time, end_time, sysplex, lpar, port_type, port_id)
    
    def get_ports_throughput_metrics(self, start_time: datetime = None, end_time: datetime = None,
                                   sysplex: str = None, lpar: str = None, port_type: str = None,
                                   port_id: str = None) -> List[Dict]:
        """Get ports throughput metrics with optional filters"""
        return self.query_dao.get_ports_throughput_metrics(start_time, end_time, sysplex, lpar, port_type, port_id)
    
    def get_volumes_utilization_metrics(self, start_time: datetime = None, end_time: datetime = None,
                                      sysplex: str = None, lpar: str = None, volume_type: str = None,
                                      volume_id: str = None) -> List[Dict]:
        """Get volumes utilization metrics with optional filters"""
        return self.query_dao.get_volumes_utilization_metrics(start_time, end_time, sysplex, lpar, volume_type, volume_id)
    
    def get_volumes_iops_metrics(self, start_time: datetime = None, end_time: datetime = None,
                               sysplex: str = None, lpar: str = None, volume_type: str = None,
                               volume_id: str = None) -> List[Dict]:
        """Get volumes IOPS metrics with optional filters"""
        return self.query_dao.get_volumes_iops_metrics(start_time, end_time, sysplex, lpar, volume_type, volume_id)
    
    def get_top_cpu_consumers(self, start_time: datetime, end_time: datetime, limit: int = 10) -> List[Dict]:
        """Get top CPU consuming LPARs in the time range"""
        return self.query_dao.get_top_cpu_consumers(start_time, end_time, limit)
    
    def get_top_memory_consumers(self, start_time: datetime, end_time: datetime, limit: int = 10) -> List[Dict]:
        """Get top memory consuming LPARs in the time range"""
        return self.query_dao.get_top_memory_consumers(start_time, end_time, limit)
    
    def get_device_performance_summary(self, start_time: datetime, end_time: datetime) -> Dict:
        """Get device performance summary including utilization and response times"""
        return self.query_dao.get_device_performance_summary(start_time, end_time)
    
    def get_hourly_metrics_summary(self, start_time: datetime, end_time: datetime, metric_type: str = 'cpu') -> List[Dict]:
        """Get hourly aggregated metrics for trend analysis"""
        return self.query_dao.get_hourly_metrics_summary(start_time, end_time, metric_type)
    
    # Maintenance methods (delegate to MaintenanceDAO)
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data beyond retention period"""
        return self.maintenance_dao.cleanup_old_data(days_to_keep)
    
    def vacuum_tables(self):
        """Optimize all tables for better performance"""
        return self.maintenance_dao.vacuum_tables()
    
    def get_table_sizes(self) -> dict:
        """Get size information for all tables"""
        return self.maintenance_dao.get_table_sizes()
    
    def analyze_table_statistics(self, table_name: str) -> dict:
        """Get detailed statistics for a specific table"""
        return self.maintenance_dao.analyze_table_statistics(table_name)
    
    def backup_table(self, table_name: str, backup_file: str):
        """Create a backup of a specific table"""
        return self.maintenance_dao.backup_table(table_name, backup_file)
    
    def truncate_table(self, table_name: str):
        """Truncate a specific table (removes all data)"""
        return self.maintenance_dao.truncate_table(table_name)
    
    # Additional convenience methods
    def test_connection(self) -> bool:
        """Test if database connection is working"""
        return self.metrics_dao.connection_manager.test_connection()
    
    def drop_all_tables(self):
        """Drop all tables (use with caution)"""
        return self.initializer.drop_all_tables()