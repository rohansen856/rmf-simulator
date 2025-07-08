from datetime import datetime
from mysql.connector import Error
from utils.logger import logger
from .connection import DatabaseConnection
from .config import DatabaseConfig

class MetricsDAO:
    """Data Access Object for metrics operations"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.connection_manager = DatabaseConnection(config)
    
    def insert_cpu_metric(self, timestamp: datetime, sysplex: str, lpar: str, 
                         cpu_type: str, utilization_percent: float):
        """Insert CPU utilization metric"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO cpu_metrics 
                    (timestamp, sysplex, lpar, cpu_type, utilization_percent)
                    VALUES (%s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, cpu_type, utilization_percent))
                
        except Error as e:
            logger.error(f"Error inserting CPU metric: {e}")
            raise
    
    def insert_memory_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                           memory_type: str, usage_bytes: int):
        """Insert memory usage metric"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO memory_metrics 
                    (timestamp, sysplex, lpar, memory_type, usage_bytes)
                    VALUES (%s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, memory_type, usage_bytes))
                
        except Error as e:
            logger.error(f"Error inserting memory metric: {e}")
            raise
    
    def insert_ldev_utilization_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                     device_id: str, utilization_percent: float):
        """Insert LDEV utilization metric"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO ldev_utilization_metrics 
                    (timestamp, sysplex, lpar, device_id, utilization_percent)
                    VALUES (%s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, device_id, utilization_percent))
                
        except Error as e:
            logger.error(f"Error inserting LDEV utilization metric: {e}")
            raise
    
    def insert_ldev_response_time_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                       device_type: str, response_time_seconds: float):
        """Insert LDEV response time metric"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO ldev_response_time_metrics 
                    (timestamp, sysplex, lpar, device_type, response_time_seconds)
                    VALUES (%s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, device_type, response_time_seconds))
                
        except Error as e:
            logger.error(f"Error inserting LDEV response time metric: {e}")
            raise
    
    def insert_clpr_service_time_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                      cf_link: str, service_time_microseconds: float):
        """Insert CLPR service time metric"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO clpr_service_time_metrics 
                    (timestamp, sysplex, lpar, cf_link, service_time_microseconds)
                    VALUES (%s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, cf_link, service_time_microseconds))
                
        except Error as e:
            logger.error(f"Error inserting CLPR service time metric: {e}")
            raise
    
    def insert_clpr_request_rate_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                      cf_link: str, request_type: str, request_rate: float):
        """Insert CLPR request rate metric"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO clpr_request_rate_metrics 
                    (timestamp, sysplex, lpar, cf_link, request_type, request_rate)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, cf_link, request_type, request_rate))
                
        except Error as e:
            logger.error(f"Error inserting CLPR request rate metric: {e}")
            raise
    
    def insert_mpb_processing_rate_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                        queue_type: str, processing_rate: float):
        """Insert MPB processing rate metric"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO mpb_processing_rate_metrics 
                    (timestamp, sysplex, lpar, queue_type, processing_rate)
                    VALUES (%s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, queue_type, processing_rate))
                
        except Error as e:
            logger.error(f"Error inserting MPB processing rate metric: {e}")
            raise
    
    def insert_mpb_queue_depth_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                    queue_type: str, queue_depth: int):
        """Insert MPB queue depth metric"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO mpb_queue_depth_metrics 
                    (timestamp, sysplex, lpar, queue_type, queue_depth)
                    VALUES (%s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, queue_type, queue_depth))
                
        except Error as e:
            logger.error(f"Error inserting MPB queue depth metric: {e}")
            raise
    
    def insert_ports_utilization_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                       port_type: str, port_id: str, utilization_percent: float):
        """Insert ports utilization metric"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO ports_utilization_metrics 
                    (timestamp, sysplex, lpar, port_type, port_id, utilization_percent)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, port_type, port_id, utilization_percent))
                
        except Error as e:
            logger.error(f"Error inserting ports utilization metric: {e}")
            raise
    
    def insert_ports_throughput_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                     port_type: str, port_id: str, throughput_mbps: float):
        """Insert ports throughput metric"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO ports_throughput_metrics 
                    (timestamp, sysplex, lpar, port_type, port_id, throughput_mbps)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, port_type, port_id, throughput_mbps))
                
        except Error as e:
            logger.error(f"Error inserting ports throughput metric: {e}")
            raise
    
    def insert_volumes_utilization_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                        volume_type: str, volume_id: str, utilization_percent: float):
        """Insert volumes utilization metric"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO volumes_utilization_metrics 
                    (timestamp, sysplex, lpar, volume_type, volume_id, utilization_percent)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, volume_type, volume_id, utilization_percent))
                
        except Error as e:
            logger.error(f"Error inserting volumes utilization metric: {e}")
            raise
    
    def insert_volumes_iops_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                 volume_type: str, volume_id: str, iops: int):
        """Insert volumes IOPS metric"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO volumes_iops_metrics 
                    (timestamp, sysplex, lpar, volume_type, volume_id, iops)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, volume_type, volume_id, iops))
                
        except Error as e:
            logger.error(f"Error inserting volumes IOPS metric: {e}")
            raise