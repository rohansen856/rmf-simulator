# storage/storage_manager.py
from datetime import datetime
from typing import Dict, Any, List, Optional
import threading

from storage.S3.s3 import S3StorageService
from storage.mysql.service import DatabaseService
from storage.mongodb.service import MongoDBService
from utils.logger import logger


class StorageManager:
    """Manages storage operations across multiple storage backends"""
    
    def __init__(self, enable_mysql: bool = True, enable_mongodb: bool = True, enable_s3: bool = True):
        self.db_service: Optional[DatabaseService] = None
        self.mongo_service: Optional[MongoDBService] = None
        self.s3_service: Optional[S3StorageService] = None
        
        # S3 batching configuration
        self.s3_batch_buffer: List[Dict[str, Any]] = []
        self.s3_batch_size = 50
        self.last_s3_flush = datetime.now()
        self.s3_flush_interval = 60  # seconds
        self._buffer_lock = threading.Lock()
        
        self._initialize_services(enable_mysql, enable_mongodb, enable_s3)
    
    def _initialize_services(self, enable_mysql: bool, enable_mongodb: bool, enable_s3: bool):
        """Initialize storage services based on configuration"""
        if enable_mysql:
            try:
                self.db_service = DatabaseService()
                logger.info("MySQL storage service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize MySQL service: {e}")
        
        if enable_mongodb:
            try:
                self.mongo_service = MongoDBService()
                logger.info("MongoDB storage service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize MongoDB service: {e}")
        
        if enable_s3:
            try:
                self.s3_service = S3StorageService()
                logger.info("S3 storage service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize S3 service: {e}")
    
    def store_metrics(self, metrics: List[Dict[str, Any]]):
        """Store metrics to all enabled storage backends"""
        for metric in metrics:
            self._store_to_databases(metric)
            self._store_to_s3_batch(metric)
    
    def _store_to_databases(self, metric: Dict[str, Any]):
        """Store metric to MySQL and MongoDB"""
        metric_type = metric.get('metric_type')
        timestamp = datetime.fromisoformat(metric['timestamp'])
        
        try:
            # Store to MySQL
            if self.db_service:
                self._store_to_mysql(metric, metric_type, timestamp)
            
            # Store to MongoDB
            if self.mongo_service:
                self._store_to_mongodb(metric, metric_type, timestamp)
                
        except Exception as e:
            logger.error(f"Error storing metric to databases: {e}")
    
    def _store_to_mysql(self, metric: Dict[str, Any], metric_type: str, timestamp: datetime):
        """Store metric to MySQL based on metric type"""
        sysplex = metric['sysplex']
        lpar = metric['lpar']
        
        if metric_type == 'cpu_utilization':
            self.db_service.insert_cpu_metric(
                timestamp, sysplex, lpar, 
                metric['cpu_type'], metric['utilization_percent']
            )
        elif metric_type == 'memory_usage':
            self.db_service.insert_memory_metric(
                timestamp, sysplex, lpar,
                metric['memory_type'], metric['usage_bytes']
            )
        elif metric_type == 'ldev_response_time':
            self.db_service.insert_ldev_response_time_metric(
                timestamp, sysplex, lpar,
                metric['device_type'], metric['response_time_seconds']
            )
        elif metric_type == 'ldev_utilization':
            self.db_service.insert_ldev_utilization_metric(
                timestamp, sysplex, lpar,
                metric['device_id'], metric['utilization_percent']
            )
        elif metric_type == 'ports_utilization':
            self.db_service.insert_ports_utilization_metric(
                timestamp, sysplex, lpar,
                metric['port_type'], metric['port_id'], metric['utilization_percent']
            )
        elif metric_type == 'ports_throughput':
            self.db_service.insert_ports_throughput_metric(
                timestamp, sysplex, lpar,
                metric['port_type'], metric['port_id'], metric['throughput_mbps']
            )
        elif metric_type == 'clpr_service_time':
            self.db_service.insert_clpr_service_time_metric(
                timestamp, sysplex, lpar,
                metric['cf_link'], metric['service_time_microseconds']
            )
        elif metric_type == 'clpr_request_rate':
            self.db_service.insert_clpr_request_rate_metric(
                timestamp, sysplex, lpar,
                metric['cf_link'], metric['request_type'], metric['request_rate']
            )
        elif metric_type == 'mpb_processing_rate':
            self.db_service.insert_mpb_processing_rate_metric(
                timestamp, sysplex, lpar,
                metric['queue_type'], metric['processing_rate']
            )
        elif metric_type == 'mpb_queue_depth':
            self.db_service.insert_mpb_queue_depth_metric(
                timestamp, sysplex, lpar,
                metric['queue_type'], metric['queue_depth']
            )
        elif metric_type == 'volumes_utilization':
            self.db_service.insert_volumes_utilization_metric(
                timestamp, sysplex, lpar,
                metric['volume_type'], metric['volume_id'], metric['utilization_percent']
            )
        elif metric_type == 'volumes_iops':
            self.db_service.insert_volumes_iops_metric(
                timestamp, sysplex, lpar,
                metric['volume_type'], metric['volume_id'], metric['iops']
            )
    
    def _store_to_mongodb(self, metric: Dict[str, Any], metric_type: str, timestamp: datetime):
        """Store metric to MongoDB based on metric type"""
        sysplex = metric['sysplex']
        lpar = metric['lpar']
        
        if metric_type == 'cpu_utilization':
            self.mongo_service.insert_cpu_metric(
                timestamp, sysplex, lpar,
                metric['cpu_type'], metric['utilization_percent']
            )
        elif metric_type == 'memory_usage':
            self.mongo_service.insert_memory_metric(
                timestamp, sysplex, lpar,
                metric['memory_type'], metric['usage_bytes']
            )
        elif metric_type == 'ldev_response_time':
            self.mongo_service.insert_ldev_response_time_metric(
                timestamp, sysplex, lpar,
                metric['device_type'], metric['response_time_seconds']
            )
        elif metric_type == 'ldev_utilization':
            self.mongo_service.insert_ldev_utilization_metric(
                timestamp, sysplex, lpar,
                metric['device_id'], metric['utilization_percent']
            )
        elif metric_type == 'ports_utilization':
            self.mongo_service.insert_ports_utilization_metric(
                timestamp, sysplex, lpar,
                metric['port_type'], metric['port_id'], metric['utilization_percent']
            )
        elif metric_type == 'ports_throughput':
            self.mongo_service.insert_ports_throughput_metric(
                timestamp, sysplex, lpar,
                metric['port_type'], metric['port_id'], metric['throughput_mbps']
            )
        elif metric_type == 'clpr_service_time':
            self.mongo_service.insert_clpr_service_time_metric(
                timestamp, sysplex, lpar,
                metric['cf_link'], metric['service_time_microseconds']
            )
        elif metric_type == 'clpr_request_rate':
            self.mongo_service.insert_clpr_request_rate_metric(
                timestamp, sysplex, lpar,
                metric['cf_link'], metric['request_type'], metric['request_rate']
            )
        elif metric_type == 'mpb_processing_rate':
            self.mongo_service.insert_mpb_processing_rate_metric(
                timestamp, sysplex, lpar,
                metric['queue_type'], metric['processing_rate']
            )
        elif metric_type == 'mpb_queue_depth':
            self.mongo_service.insert_mpb_queue_depth_metric(
                timestamp, sysplex, lpar,
                metric['queue_type'], metric['queue_depth']
            )
        elif metric_type == 'volumes_utilization':
            self.mongo_service.insert_volumes_utilization_metric(
                timestamp, sysplex, lpar,
                metric['volume_type'], metric['volume_id'], metric['utilization_percent']
            )
        elif metric_type == 'volumes_iops':
            self.mongo_service.insert_volumes_iops_metric(
                timestamp, sysplex, lpar,
                metric['volume_type'], metric['volume_id'], metric['iops']
            )
    
    def _store_to_s3_batch(self, metric: Dict[str, Any]):
        """Add metric to S3 batch buffer"""
        if not self.s3_service:
            return
        
        with self._buffer_lock:
            self.s3_batch_buffer.append(metric)
            
            # Check if we need to flush the batch
            current_time = datetime.now()
            if (len(self.s3_batch_buffer) >= self.s3_batch_size or 
                (current_time - self.last_s3_flush).total_seconds() > self.s3_flush_interval):
                self._flush_s3_batch()
    
    def _flush_s3_batch(self):
        """Flush the S3 batch buffer"""
        if not self.s3_service or not self.s3_batch_buffer:
            return
        
        try:
            self.s3_service.batch_store_metrics(self.s3_batch_buffer.copy())
            logger.debug(f"Flushed {len(self.s3_batch_buffer)} metrics to S3")
            self.s3_batch_buffer.clear()
            self.last_s3_flush = datetime.now()
        except Exception as e:
            logger.error(f"Error flushing S3 batch: {e}")
    
    def force_flush(self):
        """Force flush all pending operations"""
        with self._buffer_lock:
            self._flush_s3_batch()
    
    def close(self):
        """Clean up resources"""
        self.force_flush()
        
        if self.db_service:
            try:
                self.db_service.close()
            except Exception as e:
                logger.error(f"Error closing MySQL service: {e}")
        
        if self.mongo_service:
            try:
                self.mongo_service.close()
            except Exception as e:
                logger.error(f"Error closing MongoDB service: {e}")
        
        if self.s3_service:
            try:
                self.s3_service.close()
            except Exception as e:
                logger.error(f"Error closing S3 service: {e}")