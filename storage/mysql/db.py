import mysql.connector
from mysql.connector import Error
import json
from utils.logger import logger
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import os
from contextlib import contextmanager

@dataclass
class DatabaseConfig:
    host: str = os.getenv('MYSQL_HOST', 'localhost')
    port: int = int(os.getenv('MYSQL_PORT', '3306'))
    database: str = os.getenv('MYSQL_DATABASE', 'rmf_monitoring')
    user: str = os.getenv('MYSQL_USER', 'rmf_user')
    password: str = os.getenv('MYSQL_PASSWORD', 'rmf_password')
    root_password: str = os.getenv('MYSQL_ROOT_PASSWORD', 'root_password')

class DatabaseService:
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self._connection_pool = None
        self.initialize_database()
    
    def _get_root_connection(self):
        """Get connection as root to create database and user"""
        try:
            connection = mysql.connector.connect(
                host=self.config.host,
                port=self.config.port,
                user='root',
                password=self.config.root_password,
                autocommit=True
            )
            return connection
        except Error as e:
            logger.error(f"Error connecting to MySQL as root: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool"""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password,
                autocommit=True
            )
            yield connection
        except Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def initialize_database(self):
        """Initialize database, user, and tables if they don't exist"""
        try:
            # Create database and user if they don't exist
            self._create_database_and_user()
            
            # Create tables
            self._create_tables()
            
            logger.info("Database initialization completed successfully")
            
        except Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _create_database_and_user(self):
        """Create database and user if they don't exist"""
        try:
            with self._get_root_connection() as connection:
                cursor = connection.cursor()
                
                # Create database
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config.database}")
                logger.info(f"Database '{self.config.database}' created or already exists")
                
                # Create user and grant privileges
                cursor.execute(f"""
                    CREATE USER IF NOT EXISTS '{self.config.user}'@'%' 
                    IDENTIFIED BY '{self.config.password}'
                """)
                
                cursor.execute(f"""
                    GRANT ALL PRIVILEGES ON {self.config.database}.* 
                    TO '{self.config.user}'@'%'
                """)

                cursor.execute(f"""
                    CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '{self.config.root_password}';
                    GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
                """)
                
                cursor.execute("FLUSH PRIVILEGES")
                logger.info(f"User '{self.config.user}' created and granted privileges")
                
        except Error as e:
            logger.error(f"Error creating database and user: {e}")
            raise
    
    def _create_tables(self):
        """Create all required tables"""
        tables = {
            'cpu_metrics': """
                CREATE TABLE IF NOT EXISTS cpu_metrics (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME(3) NOT NULL,
                    sysplex VARCHAR(50) NOT NULL,
                    lpar VARCHAR(50) NOT NULL,
                    cpu_type VARCHAR(50) NOT NULL,
                    utilization_percent DECIMAL(5,2) NOT NULL,
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_lpar_cpu (lpar, cpu_type),
                    INDEX idx_sysplex_timestamp (sysplex, timestamp)
                )
            """,
            
            'memory_metrics': """
                CREATE TABLE IF NOT EXISTS memory_metrics (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME(3) NOT NULL,
                    sysplex VARCHAR(50) NOT NULL,
                    lpar VARCHAR(50) NOT NULL,
                    memory_type VARCHAR(50) NOT NULL,
                    usage_bytes BIGINT NOT NULL,
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_lpar_memory (lpar, memory_type),
                    INDEX idx_sysplex_timestamp (sysplex, timestamp)
                )
            """,
            
            'ldev_utilization_metrics': """
                CREATE TABLE IF NOT EXISTS ldev_utilization_metrics (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME(3) NOT NULL,
                    sysplex VARCHAR(50) NOT NULL,
                    lpar VARCHAR(50) NOT NULL,
                    device_id VARCHAR(50) NOT NULL,
                    utilization_percent DECIMAL(5,2) NOT NULL,
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_device (device_id),
                    INDEX idx_lpar_timestamp (lpar, timestamp)
                )
            """,
            
            'ldev_response_time_metrics': """
                CREATE TABLE IF NOT EXISTS ldev_response_time_metrics (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME(3) NOT NULL,
                    sysplex VARCHAR(50) NOT NULL,
                    lpar VARCHAR(50) NOT NULL,
                    device_type VARCHAR(50) NOT NULL,
                    response_time_seconds DECIMAL(10,6) NOT NULL,
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_device_type (device_type),
                    INDEX idx_lpar_timestamp (lpar, timestamp)
                )
            """,
            
            'clpr_service_time_metrics': """
                CREATE TABLE IF NOT EXISTS clpr_service_time_metrics (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME(3) NOT NULL,
                    sysplex VARCHAR(50) NOT NULL,
                    lpar VARCHAR(50) NOT NULL,
                    cf_link VARCHAR(50) NOT NULL,
                    service_time_microseconds DECIMAL(10,3) NOT NULL,
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_cf_link (cf_link),
                    INDEX idx_lpar_timestamp (lpar, timestamp)
                )
            """,
            
            'clpr_request_rate_metrics': """
                CREATE TABLE IF NOT EXISTS clpr_request_rate_metrics (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME(3) NOT NULL,
                    sysplex VARCHAR(50) NOT NULL,
                    lpar VARCHAR(50) NOT NULL,
                    cf_link VARCHAR(50) NOT NULL,
                    request_type VARCHAR(50) NOT NULL,
                    request_rate DECIMAL(10,2) NOT NULL,
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_cf_link_type (cf_link, request_type),
                    INDEX idx_lpar_timestamp (lpar, timestamp)
                )
            """,
            
            'mpb_processing_rate_metrics': """
                CREATE TABLE IF NOT EXISTS mpb_processing_rate_metrics (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME(3) NOT NULL,
                    sysplex VARCHAR(50) NOT NULL,
                    lpar VARCHAR(50) NOT NULL,
                    queue_type VARCHAR(50) NOT NULL,
                    processing_rate DECIMAL(10,2) NOT NULL,
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_queue_type (queue_type),
                    INDEX idx_lpar_timestamp (lpar, timestamp)
                )
            """,
            
            'mpb_queue_depth_metrics': """
                CREATE TABLE IF NOT EXISTS mpb_queue_depth_metrics (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME(3) NOT NULL,
                    sysplex VARCHAR(50) NOT NULL,
                    lpar VARCHAR(50) NOT NULL,
                    queue_type VARCHAR(50) NOT NULL,
                    queue_depth INT NOT NULL,
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_queue_type (queue_type),
                    INDEX idx_lpar_timestamp (lpar, timestamp)
                )
            """,
            
            'ports_utilization_metrics': """
                CREATE TABLE IF NOT EXISTS ports_utilization_metrics (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME(3) NOT NULL,
                    sysplex VARCHAR(50) NOT NULL,
                    lpar VARCHAR(50) NOT NULL,
                    port_type VARCHAR(50) NOT NULL,
                    port_id VARCHAR(50) NOT NULL,
                    utilization_percent DECIMAL(5,2) NOT NULL,
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_port (port_type, port_id),
                    INDEX idx_lpar_timestamp (lpar, timestamp)
                )
            """,
            
            'ports_throughput_metrics': """
                CREATE TABLE IF NOT EXISTS ports_throughput_metrics (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME(3) NOT NULL,
                    sysplex VARCHAR(50) NOT NULL,
                    lpar VARCHAR(50) NOT NULL,
                    port_type VARCHAR(50) NOT NULL,
                    port_id VARCHAR(50) NOT NULL,
                    throughput_mbps DECIMAL(10,2) NOT NULL,
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_port (port_type, port_id),
                    INDEX idx_lpar_timestamp (lpar, timestamp)
                )
            """,
            
            'volumes_utilization_metrics': """
                CREATE TABLE IF NOT EXISTS volumes_utilization_metrics (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME(3) NOT NULL,
                    sysplex VARCHAR(50) NOT NULL,
                    lpar VARCHAR(50) NOT NULL,
                    volume_type VARCHAR(50) NOT NULL,
                    volume_id VARCHAR(50) NOT NULL,
                    utilization_percent DECIMAL(5,2) NOT NULL,
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_volume (volume_type, volume_id),
                    INDEX idx_lpar_timestamp (lpar, timestamp)
                )
            """,
            
            'volumes_iops_metrics': """
                CREATE TABLE IF NOT EXISTS volumes_iops_metrics (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME(3) NOT NULL,
                    sysplex VARCHAR(50) NOT NULL,
                    lpar VARCHAR(50) NOT NULL,
                    volume_type VARCHAR(50) NOT NULL,
                    volume_id VARCHAR(50) NOT NULL,
                    iops INT NOT NULL,
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_volume (volume_type, volume_id),
                    INDEX idx_lpar_timestamp (lpar, timestamp)
                )
            """
        }
        
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                for table_name, table_sql in tables.items():
                    cursor.execute(table_sql)
                    logger.info(f"Table '{table_name}' created or already exists")
                    
        except Error as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def insert_cpu_metric(self, timestamp: datetime, sysplex: str, lpar: str, 
                         cpu_type: str, utilization_percent: float):
        """Insert CPU utilization metric"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO cpu_metrics 
                    (timestamp, sysplex, lpar, cpu_type, utilization_percent)
                    VALUES (%s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, cpu_type, utilization_percent))
                
        except Error as e:
            logger.error(f"Error inserting CPU metric: {e}")
    
    def insert_memory_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                           memory_type: str, usage_bytes: int):
        """Insert memory usage metric"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO memory_metrics 
                    (timestamp, sysplex, lpar, memory_type, usage_bytes)
                    VALUES (%s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, memory_type, usage_bytes))
                
        except Error as e:
            logger.error(f"Error inserting memory metric: {e}")
    
    def insert_ldev_utilization_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                     device_id: str, utilization_percent: float):
        """Insert LDEV utilization metric"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO ldev_utilization_metrics 
                    (timestamp, sysplex, lpar, device_id, utilization_percent)
                    VALUES (%s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, device_id, utilization_percent))
                
        except Error as e:
            logger.error(f"Error inserting LDEV utilization metric: {e}")
    
    def insert_ldev_response_time_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                       device_type: str, response_time_seconds: float):
        """Insert LDEV response time metric"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO ldev_response_time_metrics 
                    (timestamp, sysplex, lpar, device_type, response_time_seconds)
                    VALUES (%s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, device_type, response_time_seconds))
                
        except Error as e:
            logger.error(f"Error inserting LDEV response time metric: {e}")
    
    def insert_clpr_service_time_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                      cf_link: str, service_time_microseconds: float):
        """Insert CLPR service time metric"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO clpr_service_time_metrics 
                    (timestamp, sysplex, lpar, cf_link, service_time_microseconds)
                    VALUES (%s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, cf_link, service_time_microseconds))
                
        except Error as e:
            logger.error(f"Error inserting CLPR service time metric: {e}")
    
    def insert_clpr_request_rate_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                      cf_link: str, request_type: str, request_rate: float):
        """Insert CLPR request rate metric"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO clpr_request_rate_metrics 
                    (timestamp, sysplex, lpar, cf_link, request_type, request_rate)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, cf_link, request_type, request_rate))
                
        except Error as e:
            logger.error(f"Error inserting CLPR request rate metric: {e}")
    
    def insert_mpb_processing_rate_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                        queue_type: str, processing_rate: float):
        """Insert MPB processing rate metric"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO mpb_processing_rate_metrics 
                    (timestamp, sysplex, lpar, queue_type, processing_rate)
                    VALUES (%s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, queue_type, processing_rate))
                
        except Error as e:
            logger.error(f"Error inserting MPB processing rate metric: {e}")
    
    def insert_mpb_queue_depth_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                    queue_type: str, queue_depth: int):
        """Insert MPB queue depth metric"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO mpb_queue_depth_metrics 
                    (timestamp, sysplex, lpar, queue_type, queue_depth)
                    VALUES (%s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, queue_type, queue_depth))
                
        except Error as e:
            logger.error(f"Error inserting MPB queue depth metric: {e}")
    
    def insert_ports_utilization_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                       port_type: str, port_id: str, utilization_percent: float):
        """Insert ports utilization metric"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO ports_utilization_metrics 
                    (timestamp, sysplex, lpar, port_type, port_id, utilization_percent)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, port_type, port_id, utilization_percent))
                
        except Error as e:
            logger.error(f"Error inserting ports utilization metric: {e}")
    
    def insert_ports_throughput_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                     port_type: str, port_id: str, throughput_mbps: float):
        """Insert ports throughput metric"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO ports_throughput_metrics 
                    (timestamp, sysplex, lpar, port_type, port_id, throughput_mbps)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, port_type, port_id, throughput_mbps))
                
        except Error as e:
            logger.error(f"Error inserting ports throughput metric: {e}")
    
    def insert_volumes_utilization_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                        volume_type: str, volume_id: str, utilization_percent: float):
        """Insert volumes utilization metric"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO volumes_utilization_metrics 
                    (timestamp, sysplex, lpar, volume_type, volume_id, utilization_percent)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, volume_type, volume_id, utilization_percent))
                
        except Error as e:
            logger.error(f"Error inserting volumes utilization metric: {e}")
    
    def insert_volumes_iops_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                 volume_type: str, volume_id: str, iops: int):
        """Insert volumes IOPS metric"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO volumes_iops_metrics 
                    (timestamp, sysplex, lpar, volume_type, volume_id, iops)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (timestamp, sysplex, lpar, volume_type, volume_id, iops))
                
        except Error as e:
            logger.error(f"Error inserting volumes IOPS metric: {e}")
    
    def get_metrics_summary(self, start_time: datetime = None, end_time: datetime = None) -> Dict:
        """Get a summary of metrics for a time range"""
        try:
            with self.get_connection() as connection:
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
                tables = [
                    'cpu_metrics', 'memory_metrics', 'ldev_utilization_metrics',
                    'ldev_response_time_metrics', 'clpr_service_time_metrics',
                    'clpr_request_rate_metrics', 'mpb_processing_rate_metrics',
                    'mpb_queue_depth_metrics', 'ports_utilization_metrics',
                    'ports_throughput_metrics', 'volumes_utilization_metrics',
                    'volumes_iops_metrics'
                ]
                
                summary = {}
                for table in tables:
                    query = f"SELECT COUNT(*) as count FROM {table} WHERE 1=1{time_filter}"
                    cursor.execute(query, params)
                    result = cursor.fetchone()
                    summary[table] = result['count']
                
                return summary
                
        except Error as e:
            logger.error(f"Error getting metrics summary: {e}")
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data beyond retention period"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                tables = [
                    'cpu_metrics', 'memory_metrics', 'ldev_utilization_metrics',
                    'ldev_response_time_metrics', 'clpr_service_time_metrics',
                    'clpr_request_rate_metrics', 'mpb_processing_rate_metrics',
                    'mpb_queue_depth_metrics', 'ports_utilization_metrics',
                    'ports_throughput_metrics', 'volumes_utilization_metrics',
                    'volumes_iops_metrics'
                ]
                
                for table in tables:
                    query = f"""
                        DELETE FROM {table} 
                        WHERE timestamp < DATE_SUB(NOW(), INTERVAL %s DAY)
                    """
                    cursor.execute(query, (days_to_keep,))
                    deleted_count = cursor.rowcount
                    logger.info(f"Cleaned up {deleted_count} old records from {table}")
                    
        except Error as e:
            logger.error(f"Error cleaning up old data: {e}")