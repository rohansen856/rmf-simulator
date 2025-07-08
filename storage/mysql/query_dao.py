from datetime import datetime
from typing import Dict, List, Optional, Any
from mysql.connector import Error
from utils.logger import logger
from .connection import DatabaseConnection
from .config import DatabaseConfig
from .schema import TABLE_NAMES

class QueryDAO:
    """Data Access Object for query operations"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.connection_manager = DatabaseConnection(config)
    
    def get_metrics_summary(self, start_time: datetime = None, end_time: datetime = None) -> Dict:
        """Get a summary of metrics for a time range"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                # Build time filter
                time_filter = ""
                params = []
                if start_time:
                    time_filter += " AND timestamp >= %s"
                    params.append(start_time)
                if end_time:
                    time_filter += " AND timestamp <= %s"
                    params.append(end_time)
                
                # Get record counts for each table
                summary = {}
                for table in TABLE_NAMES:
                    query = f"SELECT COUNT(*) as count FROM {table} WHERE 1=1{time_filter}"
                    cursor.execute(query, params)
                    result = cursor.fetchone()
                    summary[table] = result['count']
                
                return summary
                
        except Error as e:
            logger.error(f"Error getting metrics summary: {e}")
            return {}
    
    def get_cpu_metrics(self, start_time: datetime = None, end_time: datetime = None, 
                       sysplex: str = None, lpar: str = None) -> List[Dict]:
        """Get CPU metrics with optional filters"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                query = "SELECT * FROM cpu_metrics WHERE 1=1"
                params = []
                
                if start_time:
                    query += " AND timestamp >= %s"
                    params.append(start_time)
                if end_time:
                    query += " AND timestamp <= %s"
                    params.append(end_time)
                if sysplex:
                    query += " AND sysplex = %s"
                    params.append(sysplex)
                if lpar:
                    query += " AND lpar = %s"
                    params.append(lpar)
                
                query += " ORDER BY timestamp DESC"
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error getting CPU metrics: {e}")
            return []
    
    def get_memory_metrics(self, start_time: datetime = None, end_time: datetime = None,
                          sysplex: str = None, lpar: str = None) -> List[Dict]:
        """Get memory metrics with optional filters"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                query = "SELECT * FROM memory_metrics WHERE 1=1"
                params = []
                
                if start_time:
                    query += " AND timestamp >= %s"
                    params.append(start_time)
                if end_time:
                    query += " AND timestamp <= %s"
                    params.append(end_time)
                if sysplex:
                    query += " AND sysplex = %s"
                    params.append(sysplex)
                if lpar:
                    query += " AND lpar = %s"
                    params.append(lpar)
                
                query += " ORDER BY timestamp DESC"
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error getting memory metrics: {e}")
            return []
    
    def get_ldev_utilization_metrics(self, start_time: datetime = None, end_time: datetime = None,
                                   sysplex: str = None, lpar: str = None, device_id: str = None) -> List[Dict]:
        """Get LDEV utilization metrics with optional filters"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                query = "SELECT * FROM ldev_utilization_metrics WHERE 1=1"
                params = []
                
                if start_time:
                    query += " AND timestamp >= %s"
                    params.append(start_time)
                if end_time:
                    query += " AND timestamp <= %s"
                    params.append(end_time)
                if sysplex:
                    query += " AND sysplex = %s"
                    params.append(sysplex)
                if lpar:
                    query += " AND lpar = %s"
                    params.append(lpar)
                if device_id:
                    query += " AND device_id = %s"
                    params.append(device_id)
                
                query += " ORDER BY timestamp DESC"
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error getting LDEV utilization metrics: {e}")
            return []
    
    def get_average_cpu_utilization(self, start_time: datetime, end_time: datetime,
                                   sysplex: str = None, lpar: str = None) -> Dict:
        """Get average CPU utilization for a time range"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                query = """
                    SELECT 
                        sysplex,
                        lpar,
                        cpu_type,
                        AVG(utilization_percent) as avg_utilization,
                        MAX(utilization_percent) as max_utilization,
                        MIN(utilization_percent) as min_utilization
                    FROM cpu_metrics 
                    WHERE timestamp >= %s AND timestamp <= %s
                """
                params = [start_time, end_time]
                
                if sysplex:
                    query += " AND sysplex = %s"
                    params.append(sysplex)
                if lpar:
                    query += " AND lpar = %s"
                    params.append(lpar)
                
                query += " GROUP BY sysplex, lpar, cpu_type"
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error getting average CPU utilization: {e}")
            return {}
    
    def get_peak_memory_usage(self, start_time: datetime, end_time: datetime,
                             sysplex: str = None, lpar: str = None) -> Dict:
        """Get peak memory usage for a time range"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                query = """
                    SELECT 
                        sysplex,
                        lpar,
                        memory_type,
                        MAX(usage_bytes) as peak_usage,
                        AVG(usage_bytes) as avg_usage
                    FROM memory_metrics 
                    WHERE timestamp >= %s AND timestamp <= %s
                """
                params = [start_time, end_time]
                
                if sysplex:
                    query += " AND sysplex = %s"
                    params.append(sysplex)
                if lpar:
                    query += " AND lpar = %s"
                    params.append(lpar)
                
                query += " GROUP BY sysplex, lpar, memory_type"
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error getting peak memory usage: {e}")
            return {}
    
    def get_system_health_summary(self, start_time: datetime, end_time: datetime) -> Dict:
        """Get comprehensive system health summary"""
        try:
            summary = {
                'cpu_avg': self.get_average_cpu_utilization(start_time, end_time),
                'memory_peak': self.get_peak_memory_usage(start_time, end_time),
                'record_counts': self.get_metrics_summary(start_time, end_time)
            }
            return summary
            
        except Error as e:
            logger.error(f"Error getting system health summary: {e}")
            return {}
    
    def get_ldev_response_time_metrics(self, start_time: datetime = None, end_time: datetime = None,
                                     sysplex: str = None, lpar: str = None, device_type: str = None) -> List[Dict]:
        """Get LDEV response time metrics with optional filters"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                query = "SELECT * FROM ldev_response_time_metrics WHERE 1=1"
                params = []
                
                if start_time:
                    query += " AND timestamp >= %s"
                    params.append(start_time)
                if end_time:
                    query += " AND timestamp <= %s"
                    params.append(end_time)
                if sysplex:
                    query += " AND sysplex = %s"
                    params.append(sysplex)
                if lpar:
                    query += " AND lpar = %s"
                    params.append(lpar)
                if device_type:
                    query += " AND device_type = %s"
                    params.append(device_type)
                
                query += " ORDER BY timestamp DESC"
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error getting LDEV response time metrics: {e}")
            return []
    
    def get_clpr_service_time_metrics(self, start_time: datetime = None, end_time: datetime = None,
                                    sysplex: str = None, lpar: str = None, cf_link: str = None) -> List[Dict]:
        """Get CLPR service time metrics with optional filters"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                query = "SELECT * FROM clpr_service_time_metrics WHERE 1=1"
                params = []
                
                if start_time:
                    query += " AND timestamp >= %s"
                    params.append(start_time)
                if end_time:
                    query += " AND timestamp <= %s"
                    params.append(end_time)
                if sysplex:
                    query += " AND sysplex = %s"
                    params.append(sysplex)
                if lpar:
                    query += " AND lpar = %s"
                    params.append(lpar)
                if cf_link:
                    query += " AND cf_link = %s"
                    params.append(cf_link)
                
                query += " ORDER BY timestamp DESC"
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error getting CLPR service time metrics: {e}")
            return []
    
    def get_clpr_request_rate_metrics(self, start_time: datetime = None, end_time: datetime = None,
                                    sysplex: str = None, lpar: str = None, cf_link: str = None,
                                    request_type: str = None) -> List[Dict]:
        """Get CLPR request rate metrics with optional filters"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                query = "SELECT * FROM clpr_request_rate_metrics WHERE 1=1"
                params = []
                
                if start_time:
                    query += " AND timestamp >= %s"
                    params.append(start_time)
                if end_time:
                    query += " AND timestamp <= %s"
                    params.append(end_time)
                if sysplex:
                    query += " AND sysplex = %s"
                    params.append(sysplex)
                if lpar:
                    query += " AND lpar = %s"
                    params.append(lpar)
                if cf_link:
                    query += " AND cf_link = %s"
                    params.append(cf_link)
                if request_type:
                    query += " AND request_type = %s"
                    params.append(request_type)
                
                query += " ORDER BY timestamp DESC"
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error getting CLPR request rate metrics: {e}")
            return []
    
    def get_mpb_processing_rate_metrics(self, start_time: datetime = None, end_time: datetime = None,
                                      sysplex: str = None, lpar: str = None, queue_type: str = None) -> List[Dict]:
        """Get MPB processing rate metrics with optional filters"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                query = "SELECT * FROM mpb_processing_rate_metrics WHERE 1=1"
                params = []
                
                if start_time:
                    query += " AND timestamp >= %s"
                    params.append(start_time)
                if end_time:
                    query += " AND timestamp <= %s"
                    params.append(end_time)
                if sysplex:
                    query += " AND sysplex = %s"
                    params.append(sysplex)
                if lpar:
                    query += " AND lpar = %s"
                    params.append(lpar)
                if queue_type:
                    query += " AND queue_type = %s"
                    params.append(queue_type)
                
                query += " ORDER BY timestamp DESC"
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error getting MPB processing rate metrics: {e}")
            return []
    
    def get_mpb_queue_depth_metrics(self, start_time: datetime = None, end_time: datetime = None,
                                  sysplex: str = None, lpar: str = None, queue_type: str = None) -> List[Dict]:
        """Get MPB queue depth metrics with optional filters"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                query = "SELECT * FROM mpb_queue_depth_metrics WHERE 1=1"
                params = []
                
                if start_time:
                    query += " AND timestamp >= %s"
                    params.append(start_time)
                if end_time:
                    query += " AND timestamp <= %s"
                    params.append(end_time)
                if sysplex:
                    query += " AND sysplex = %s"
                    params.append(sysplex)
                if lpar:
                    query += " AND lpar = %s"
                    params.append(lpar)
                if queue_type:
                    query += " AND queue_type = %s"
                    params.append(queue_type)
                
                query += " ORDER BY timestamp DESC"
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error getting MPB queue depth metrics: {e}")
            return []
    
    def get_ports_utilization_metrics(self, start_time: datetime = None, end_time: datetime = None,
                                    sysplex: str = None, lpar: str = None, port_type: str = None,
                                    port_id: str = None) -> List[Dict]:
        """Get ports utilization metrics with optional filters"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                query = "SELECT * FROM ports_utilization_metrics WHERE 1=1"
                params = []
                
                if start_time:
                    query += " AND timestamp >= %s"
                    params.append(start_time)
                if end_time:
                    query += " AND timestamp <= %s"
                    params.append(end_time)
                if sysplex:
                    query += " AND sysplex = %s"
                    params.append(sysplex)
                if lpar:
                    query += " AND lpar = %s"
                    params.append(lpar)
                if port_type:
                    query += " AND port_type = %s"
                    params.append(port_type)
                if port_id:
                    query += " AND port_id = %s"
                    params.append(port_id)
                
                query += " ORDER BY timestamp DESC"
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error getting ports utilization metrics: {e}")
            return []
    
    def get_ports_throughput_metrics(self, start_time: datetime = None, end_time: datetime = None,
                                   sysplex: str = None, lpar: str = None, port_type: str = None,
                                   port_id: str = None) -> List[Dict]:
        """Get ports throughput metrics with optional filters"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                query = "SELECT * FROM ports_throughput_metrics WHERE 1=1"
                params = []
                
                if start_time:
                    query += " AND timestamp >= %s"
                    params.append(start_time)
                if end_time:
                    query += " AND timestamp <= %s"
                    params.append(end_time)
                if sysplex:
                    query += " AND sysplex = %s"
                    params.append(sysplex)
                if lpar:
                    query += " AND lpar = %s"
                    params.append(lpar)
                if port_type:
                    query += " AND port_type = %s"
                    params.append(port_type)
                if port_id:
                    query += " AND port_id = %s"
                    params.append(port_id)
                
                query += " ORDER BY timestamp DESC"
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error getting ports throughput metrics: {e}")
            return []
    
    def get_volumes_utilization_metrics(self, start_time: datetime = None, end_time: datetime = None,
                                      sysplex: str = None, lpar: str = None, volume_type: str = None,
                                      volume_id: str = None) -> List[Dict]:
        """Get volumes utilization metrics with optional filters"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                query = "SELECT * FROM volumes_utilization_metrics WHERE 1=1"
                params = []
                
                if start_time:
                    query += " AND timestamp >= %s"
                    params.append(start_time)
                if end_time:
                    query += " AND timestamp <= %s"
                    params.append(end_time)
                if sysplex:
                    query += " AND sysplex = %s"
                    params.append(sysplex)
                if lpar:
                    query += " AND lpar = %s"
                    params.append(lpar)
                if volume_type:
                    query += " AND volume_type = %s"
                    params.append(volume_type)
                if volume_id:
                    query += " AND volume_id = %s"
                    params.append(volume_id)
                
                query += " ORDER BY timestamp DESC"
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error getting volumes utilization metrics: {e}")
            return []
    
    def get_volumes_iops_metrics(self, start_time: datetime = None, end_time: datetime = None,
                               sysplex: str = None, lpar: str = None, volume_type: str = None,
                               volume_id: str = None) -> List[Dict]:
        """Get volumes IOPS metrics with optional filters"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                query = "SELECT * FROM volumes_iops_metrics WHERE 1=1"
                params = []
                
                if start_time:
                    query += " AND timestamp >= %s"
                    params.append(start_time)
                if end_time:
                    query += " AND timestamp <= %s"
                    params.append(end_time)
                if sysplex:
                    query += " AND sysplex = %s"
                    params.append(sysplex)
                if lpar:
                    query += " AND lpar = %s"
                    params.append(lpar)
                if volume_type:
                    query += " AND volume_type = %s"
                    params.append(volume_type)
                if volume_id:
                    query += " AND volume_id = %s"
                    params.append(volume_id)
                
                query += " ORDER BY timestamp DESC"
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error getting volumes IOPS metrics: {e}")
            return []
    
    def get_top_cpu_consumers(self, start_time: datetime, end_time: datetime, limit: int = 10) -> List[Dict]:
        """Get top CPU consuming LPARs in the time range"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                query = """
                    SELECT 
                        sysplex,
                        lpar,
                        cpu_type,
                        AVG(utilization_percent) as avg_utilization,
                        MAX(utilization_percent) as peak_utilization,
                        COUNT(*) as sample_count
                    FROM cpu_metrics 
                    WHERE timestamp >= %s AND timestamp <= %s
                    GROUP BY sysplex, lpar, cpu_type
                    ORDER BY avg_utilization DESC
                    LIMIT %s
                """
                cursor.execute(query, (start_time, end_time, limit))
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error getting top CPU consumers: {e}")
            return []
    
    def get_top_memory_consumers(self, start_time: datetime, end_time: datetime, limit: int = 10) -> List[Dict]:
        """Get top memory consuming LPARs in the time range"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                query = """
                    SELECT 
                        sysplex,
                        lpar,
                        memory_type,
                        AVG(usage_bytes) as avg_usage,
                        MAX(usage_bytes) as peak_usage,
                        COUNT(*) as sample_count
                    FROM memory_metrics 
                    WHERE timestamp >= %s AND timestamp <= %s
                    GROUP BY sysplex, lpar, memory_type
                    ORDER BY avg_usage DESC
                    LIMIT %s
                """
                cursor.execute(query, (start_time, end_time, limit))
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error getting top memory consumers: {e}")
            return []
    
    def get_device_performance_summary(self, start_time: datetime, end_time: datetime) -> Dict:
        """Get device performance summary including utilization and response times"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                # Get LDEV utilization summary
                cursor.execute("""
                    SELECT 
                        device_id,
                        AVG(utilization_percent) as avg_utilization,
                        MAX(utilization_percent) as peak_utilization,
                        COUNT(*) as sample_count
                    FROM ldev_utilization_metrics
                    WHERE timestamp >= %s AND timestamp <= %s
                    GROUP BY device_id
                    ORDER BY avg_utilization DESC
                    LIMIT 20
                """, (start_time, end_time))
                ldev_utilization = cursor.fetchall()
                
                # Get LDEV response time summary
                cursor.execute("""
                    SELECT 
                        device_type,
                        AVG(response_time_seconds) as avg_response_time,
                        MAX(response_time_seconds) as max_response_time,
                        COUNT(*) as sample_count
                    FROM ldev_response_time_metrics
                    WHERE timestamp >= %s AND timestamp <= %s
                    GROUP BY device_type
                    ORDER BY avg_response_time DESC
                """, (start_time, end_time))
                ldev_response_time = cursor.fetchall()
                
                return {
                    'ldev_utilization': ldev_utilization,
                    'ldev_response_time': ldev_response_time
                }
                
        except Error as e:
            logger.error(f"Error getting device performance summary: {e}")
            return {}
    
    def get_hourly_metrics_summary(self, start_time: datetime, end_time: datetime, metric_type: str = 'cpu') -> List[Dict]:
        """Get hourly aggregated metrics for trend analysis"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                table_map = {
                    'cpu': 'cpu_metrics',
                    'memory': 'memory_metrics',
                    'ldev_util': 'ldev_utilization_metrics',
                    'ldev_response': 'ldev_response_time_metrics'
                }
                
                if metric_type not in table_map:
                    raise ValueError(f"Invalid metric type: {metric_type}")
                
                table = table_map[metric_type]
                
                if metric_type == 'cpu':
                    query = """
                        SELECT 
                            DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') as hour,
                            sysplex,
                            lpar,
                            cpu_type,
                            AVG(utilization_percent) as avg_value,
                            MAX(utilization_percent) as max_value,
                            COUNT(*) as sample_count
                        FROM cpu_metrics
                        WHERE timestamp >= %s AND timestamp <= %s
                        GROUP BY hour, sysplex, lpar, cpu_type
                        ORDER BY hour ASC
                    """
                elif metric_type == 'memory':
                    query = """
                        SELECT 
                            DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') as hour,
                            sysplex,
                            lpar,
                            memory_type,
                            AVG(usage_bytes) as avg_value,
                            MAX(usage_bytes) as max_value,
                            COUNT(*) as sample_count
                        FROM memory_metrics
                        WHERE timestamp >= %s AND timestamp <= %s
                        GROUP BY hour, sysplex, lpar, memory_type
                        ORDER BY hour ASC
                    """
                elif metric_type == 'ldev_util':
                    query = """
                        SELECT 
                            DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') as hour,
                            device_id,
                            AVG(utilization_percent) as avg_value,
                            MAX(utilization_percent) as max_value,
                            COUNT(*) as sample_count
                        FROM ldev_utilization_metrics
                        WHERE timestamp >= %s AND timestamp <= %s
                        GROUP BY hour, device_id
                        ORDER BY hour ASC
                    """
                elif metric_type == 'ldev_response':
                    query = """
                        SELECT 
                            DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') as hour,
                            device_type,
                            AVG(response_time_seconds) as avg_value,
                            MAX(response_time_seconds) as max_value,
                            COUNT(*) as sample_count
                        FROM ldev_response_time_metrics
                        WHERE timestamp >= %s AND timestamp <= %s
                        GROUP BY hour, device_type
                        ORDER BY hour ASC
                    """
                
                cursor.execute(query, (start_time, end_time))
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error getting hourly metrics summary: {e}")
            return []