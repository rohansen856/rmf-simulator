"""
MongoDB Query Operations
"""
from datetime import datetime
from typing import Dict, List, Optional

from utils.logger import logger


class MongoQueries:
    """Handles MongoDB query operations for metrics"""
    
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
    
    def get_metrics_summary(self, start_time: datetime = None, end_time: datetime = None) -> Dict:
        """Get a summary of metrics for a time range"""
        try:
            with self.connection_manager.get_database() as db:
                # Build time filter
                time_filter = {}
                if start_time:
                    time_filter['$gte'] = start_time
                if end_time:
                    time_filter['$lte'] = end_time
                
                filter_query = {}
                if time_filter:
                    filter_query['timestamp'] = time_filter
                
                # Get record counts for each collection
                collections = [
                    'cpu_metrics', 'memory_metrics', 'ldev_utilization_metrics',
                    'ldev_response_time_metrics', 'clpr_service_time_metrics',
                    'clpr_request_rate_metrics', 'mpb_processing_rate_metrics',
                    'mpb_queue_depth_metrics', 'ports_utilization_metrics',
                    'ports_throughput_metrics', 'volumes_utilization_metrics',
                    'volumes_iops_metrics'
                ]
                
                summary = {}
                for collection_name in collections:
                    try:
                        collection = db[collection_name]
                        count = collection.count_documents(filter_query)
                        summary[collection_name] = count
                    except Exception as e:
                        logger.error(f"Error counting documents in {collection_name}: {e}")
                        summary[collection_name] = 0
                
                return summary
                
        except Exception as e:
            logger.error(f"Error getting metrics summary: {e}")
            return {}
    
    def get_latest_metrics(self, sysplex: str = None, lpar: str = None, 
                          limit: int = 100) -> Dict[str, List[Dict]]:
        """Get latest metrics for a specific sysplex/lpar"""
        try:
            with self.connection_manager.get_database() as db:
                filter_query = {}
                if sysplex:
                    filter_query['sysplex'] = sysplex
                if lpar:
                    filter_query['lpar'] = lpar
                
                collections = [
                    'cpu_metrics', 'memory_metrics', 'ldev_utilization_metrics',
                    'ldev_response_time_metrics', 'clpr_service_time_metrics',
                    'clpr_request_rate_metrics', 'mpb_processing_rate_metrics',
                    'mpb_queue_depth_metrics', 'ports_utilization_metrics',
                    'ports_throughput_metrics', 'volumes_utilization_metrics',
                    'volumes_iops_metrics'
                ]
                
                results = {}
                for collection_name in collections:
                    try:
                        collection = db[collection_name]
                        cursor = collection.find(filter_query).sort([('timestamp', -1)]).limit(limit)
                        documents = list(cursor)
                        
                        # Convert ObjectId to string for JSON serialization
                        for doc in documents:
                            doc['_id'] = str(doc['_id'])
                        
                        results[collection_name] = documents
                    except Exception as e:
                        logger.error(f"Error fetching from {collection_name}: {e}")
                        results[collection_name] = []
                
                return results
                
        except Exception as e:
            logger.error(f"Error getting latest metrics: {e}")
            return {}
    
    def get_metrics_aggregation(self, collection_name: str, pipeline: List[Dict]) -> List[Dict]:
        """Run aggregation pipeline on specified collection"""
        try:
            with self.connection_manager.get_database() as db:
                collection = db[collection_name]
                cursor = collection.aggregate(pipeline)
                results = list(cursor)
                
                # Convert ObjectId to string for JSON serialization
                for doc in results:
                    if '_id' in doc and hasattr(doc['_id'], '__str__'):
                        doc['_id'] = str(doc['_id'])
                
                return results
                
        except Exception as e:
            logger.error(f"Error running aggregation on {collection_name}: {e}")
            return []
    
    def get_cpu_metrics_by_time_range(self, start_time: datetime, end_time: datetime, 
                                     sysplex: str = None, lpar: str = None) -> List[Dict]:
        """Get CPU metrics within a specific time range"""
        try:
            with self.connection_manager.get_database() as db:
                collection = db.cpu_metrics
                
                filter_query = {
                    'timestamp': {'$gte': start_time, '$lte': end_time}
                }
                
                if sysplex:
                    filter_query['sysplex'] = sysplex
                if lpar:
                    filter_query['lpar'] = lpar
                
                cursor = collection.find(filter_query).sort([('timestamp', 1)])
                documents = list(cursor)
                
                # Convert ObjectId to string for JSON serialization
                for doc in documents:
                    doc['_id'] = str(doc['_id'])
                
                return documents
                
        except Exception as e:
            logger.error(f"Error getting CPU metrics by time range: {e}")
            return []
    
    def get_memory_metrics_by_time_range(self, start_time: datetime, end_time: datetime,
                                        sysplex: str = None, lpar: str = None) -> List[Dict]:
        """Get memory metrics within a specific time range"""
        try:
            with self.connection_manager.get_database() as db:
                collection = db.memory_metrics
                
                filter_query = {
                    'timestamp': {'$gte': start_time, '$lte': end_time}
                }
                
                if sysplex:
                    filter_query['sysplex'] = sysplex
                if lpar:
                    filter_query['lpar'] = lpar
                
                cursor = collection.find(filter_query).sort([('timestamp', 1)])
                documents = list(cursor)
                
                # Convert ObjectId to string for JSON serialization
                for doc in documents:
                    doc['_id'] = str(doc['_id'])
                
                return documents
                
        except Exception as e:
            logger.error(f"Error getting memory metrics by time range: {e}")
            return []
    
    def get_average_utilization_by_lpar(self, collection_name: str, 
                                       start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get average utilization grouped by LPAR"""
        try:
            pipeline = [
                {
                    '$match': {
                        'timestamp': {'$gte': start_time, '$lte': end_time}
                    }
                },
                {
                    '$group': {
                        '_id': {
                            'sysplex': '$sysplex',
                            'lpar': '$lpar'
                        },
                        'avg_utilization': {'$avg': '$utilization_percent'},
                        'max_utilization': {'$max': '$utilization_percent'},
                        'min_utilization': {'$min': '$utilization_percent'},
                        'count': {'$sum': 1}
                    }
                },
                {
                    '$sort': {'avg_utilization': -1}
                }
            ]
            
            return self.get_metrics_aggregation(collection_name, pipeline)
            
        except Exception as e:
            logger.error(f"Error getting average utilization by LPAR: {e}")
            return []
    
    def get_peak_utilization_periods(self, collection_name: str, threshold: float,
                                   start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get periods where utilization exceeded threshold"""
        try:
            with self.connection_manager.get_database() as db:
                collection = db[collection_name]
                
                filter_query = {
                    'timestamp': {'$gte': start_time, '$lte': end_time},
                    'utilization_percent': {'$gte': threshold}
                }
                
                cursor = collection.find(filter_query).sort([('utilization_percent', -1)])
                documents = list(cursor)
                
                # Convert ObjectId to string for JSON serialization
                for doc in documents:
                    doc['_id'] = str(doc['_id'])
                
                return documents
                
        except Exception as e:
            logger.error(f"Error getting peak utilization periods: {e}")
            return []