"""
MongoDB CRUD Operations
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from utils.logger import logger


class MongoOperations:
    """Handles MongoDB CRUD operations for metrics"""
    
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
    
    # Individual metric insertion methods
    def insert_cpu_metric(self, timestamp: datetime, sysplex: str, lpar: str, 
                         cpu_type: str, utilization_percent: float):
        """Insert CPU utilization metric"""
        try:
            with self.connection_manager.get_database() as db:
                collection = db.cpu_metrics
                document = {
                    'timestamp': timestamp,
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'cpu_type': cpu_type,
                    'utilization_percent': utilization_percent
                }
                collection.insert_one(document)
                
        except Exception as e:
            logger.error(f"Error inserting CPU metric: {e}")
    
    def insert_memory_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                           memory_type: str, usage_bytes: int):
        """Insert memory usage metric"""
        try:
            with self.connection_manager.get_database() as db:
                collection = db.memory_metrics
                document = {
                    'timestamp': timestamp,
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'memory_type': memory_type,
                    'usage_bytes': usage_bytes
                }
                collection.insert_one(document)
                
        except Exception as e:
            logger.error(f"Error inserting memory metric: {e}")
    
    def insert_ldev_utilization_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                     device_id: str, utilization_percent: float):
        """Insert LDEV utilization metric"""
        try:
            with self.connection_manager.get_database() as db:
                collection = db.ldev_utilization_metrics
                document = {
                    'timestamp': timestamp,
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'device_id': device_id,
                    'utilization_percent': utilization_percent
                }
                collection.insert_one(document)
                
        except Exception as e:
            logger.error(f"Error inserting LDEV utilization metric: {e}")
    
    def insert_ldev_response_time_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                       device_type: str, response_time_seconds: float):
        """Insert LDEV response time metric"""
        try:
            with self.connection_manager.get_database() as db:
                collection = db.ldev_response_time_metrics
                document = {
                    'timestamp': timestamp,
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'device_type': device_type,
                    'response_time_seconds': response_time_seconds
                }
                collection.insert_one(document)
                
        except Exception as e:
            logger.error(f"Error inserting LDEV response time metric: {e}")
    
    def insert_clpr_service_time_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                      cf_link: str, service_time_microseconds: float):
        """Insert CLPR service time metric"""
        try:
            with self.connection_manager.get_database() as db:
                collection = db.clpr_service_time_metrics
                document = {
                    'timestamp': timestamp,
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'cf_link': cf_link,
                    'service_time_microseconds': service_time_microseconds
                }
                collection.insert_one(document)
                
        except Exception as e:
            logger.error(f"Error inserting CLPR service time metric: {e}")
    
    def insert_clpr_request_rate_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                      cf_link: str, request_type: str, request_rate: float):
        """Insert CLPR request rate metric"""
        try:
            with self.connection_manager.get_database() as db:
                collection = db.clpr_request_rate_metrics
                document = {
                    'timestamp': timestamp,
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'cf_link': cf_link,
                    'request_type': request_type,
                    'request_rate': request_rate
                }
                collection.insert_one(document)
                
        except Exception as e:
            logger.error(f"Error inserting CLPR request rate metric: {e}")
    
    def insert_mpb_processing_rate_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                        queue_type: str, processing_rate: float):
        """Insert MPB processing rate metric"""
        try:
            with self.connection_manager.get_database() as db:
                collection = db.mpb_processing_rate_metrics
                document = {
                    'timestamp': timestamp,
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'queue_type': queue_type,
                    'processing_rate': processing_rate
                }
                collection.insert_one(document)
                
        except Exception as e:
            logger.error(f"Error inserting MPB processing rate metric: {e}")
    
    def insert_mpb_queue_depth_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                    queue_type: str, queue_depth: int):
        """Insert MPB queue depth metric"""
        try:
            with self.connection_manager.get_database() as db:
                collection = db.mpb_queue_depth_metrics
                document = {
                    'timestamp': timestamp,
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'queue_type': queue_type,
                    'queue_depth': queue_depth
                }
                collection.insert_one(document)
                
        except Exception as e:
            logger.error(f"Error inserting MPB queue depth metric: {e}")
    
    def insert_ports_utilization_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                       port_type: str, port_id: str, utilization_percent: float):
        """Insert ports utilization metric"""
        try:
            with self.connection_manager.get_database() as db:
                collection = db.ports_utilization_metrics
                document = {
                    'timestamp': timestamp,
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'port_type': port_type,
                    'port_id': port_id,
                    'utilization_percent': utilization_percent
                }
                collection.insert_one(document)
                
        except Exception as e:
            logger.error(f"Error inserting ports utilization metric: {e}")
    
    def insert_ports_throughput_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                     port_type: str, port_id: str, throughput_mbps: float):
        """Insert ports throughput metric"""
        try:
            with self.connection_manager.get_database() as db:
                collection = db.ports_throughput_metrics
                document = {
                    'timestamp': timestamp,
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'port_type': port_type,
                    'port_id': port_id,
                    'throughput_mbps': throughput_mbps
                }
                collection.insert_one(document)
                
        except Exception as e:
            logger.error(f"Error inserting ports throughput metric: {e}")
    
    def insert_volumes_utilization_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                        volume_type: str, volume_id: str, utilization_percent: float):
        """Insert volumes utilization metric"""
        try:
            with self.connection_manager.get_database() as db:
                collection = db.volumes_utilization_metrics
                document = {
                    'timestamp': timestamp,
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'volume_type': volume_type,
                    'volume_id': volume_id,
                    'utilization_percent': utilization_percent
                }
                collection.insert_one(document)
                
        except Exception as e:
            logger.error(f"Error inserting volumes utilization metric: {e}")
    
    def insert_volumes_iops_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                 volume_type: str, volume_id: str, iops: int):
        """Insert volumes IOPS metric"""
        try:
            with self.connection_manager.get_database() as db:
                collection = db.volumes_iops_metrics
                document = {
                    'timestamp': timestamp,
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'volume_type': volume_type,
                    'volume_id': volume_id,
                    'iops': iops
                }
                collection.insert_one(document)
                
        except Exception as e:
            logger.error(f"Error inserting volumes IOPS metric: {e}")
    
    # Bulk operations
    def bulk_insert_metrics(self, collection_name: str, documents: List[Dict]):
        """Bulk insert multiple documents for better performance"""
        try:
            with self.connection_manager.get_database() as db:
                collection = db[collection_name]
                result = collection.insert_many(documents, ordered=False)
                logger.debug(f"Bulk inserted {len(result.inserted_ids)} documents to {collection_name}")
                return result.inserted_ids
                
        except Exception as e:
            logger.error(f"Error bulk inserting to {collection_name}: {e}")
            return []
    
    # Data cleanup
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data beyond retention period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            with self.connection_manager.get_database() as db:
                collections = [
                    'cpu_metrics', 'memory_metrics', 'ldev_utilization_metrics',
                    'ldev_response_time_metrics', 'clpr_service_time_metrics',
                    'clpr_request_rate_metrics', 'mpb_processing_rate_metrics',
                    'mpb_queue_depth_metrics', 'ports_utilization_metrics',
                    'ports_throughput_metrics', 'volumes_utilization_metrics',
                    'volumes_iops_metrics'
                ]
                
                total_deleted = 0
                for collection_name in collections:
                    try:
                        collection = db[collection_name]
                        result = collection.delete_many({'timestamp': {'$lt': cutoff_date}})
                        deleted_count = result.deleted_count
                        total_deleted += deleted_count
                        logger.info(f"Cleaned up {deleted_count} old records from {collection_name}")
                    except Exception as e:
                        logger.error(f"Error cleaning up {collection_name}: {e}")
                
                logger.info(f"Total records cleaned up: {total_deleted}")
                return total_deleted
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0