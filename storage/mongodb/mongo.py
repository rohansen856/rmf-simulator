import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, DuplicateKeyError
import json
from utils.logger import logger
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import os
from contextlib import contextmanager

@dataclass
class MongoConfig:
    host: str = os.getenv('MONGO_HOST', 'localhost')
    port: int = int(os.getenv('MONGO_PORT', '27017'))
    database: str = os.getenv('MONGO_DATABASE', 'rmf_monitoring')
    username: str = os.getenv('MONGO_USERNAME', 'rmf_user')
    password: str = os.getenv('MONGO_PASSWORD', 'rmf_password')
    auth_source: str = os.getenv('MONGO_AUTH_SOURCE', 'admin')
    replica_set: str = os.getenv('MONGO_REPLICA_SET', None)
    connection_timeout: int = int(os.getenv('MONGO_CONNECTION_TIMEOUT', '5000'))
    server_selection_timeout: int = int(os.getenv('MONGO_SERVER_SELECTION_TIMEOUT', '5000'))

class MongoDBService:
    def __init__(self, config: MongoConfig = None):
        self.config = config or MongoConfig()
        self.client = None
        self.database = None
        self.initialize_database()
    
    def _get_connection_string(self) -> str:
        """Build MongoDB connection string"""
        if self.config.username and self.config.password:
            auth_part = f"{self.config.username}:{self.config.password}@"
        else:
            auth_part = ""
        
        if self.config.replica_set:
            replica_part = f"?replicaSet={self.config.replica_set}"
        else:
            replica_part = ""
        
        return f"mongodb://{auth_part}{self.config.host}:{self.config.port}/{self.config.database}{replica_part}"
    
    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            connection_string = self._get_connection_string()
            self.client = MongoClient(
                connection_string,
                authSource=self.config.auth_source,
                connectTimeoutMS=self.config.connection_timeout,
                serverSelectionTimeoutMS=self.config.server_selection_timeout,
                maxPoolSize=50,
                minPoolSize=5,
                retryWrites=True,
                retryReads=True
            )
            
            # Test connection
            self.client.admin.command('ping')
            self.database = self.client[self.config.database]
            logger.info(f"Successfully connected to MongoDB: {self.config.host}:{self.config.port}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise
    
    @contextmanager
    def get_database(self):
        """Get database connection context manager"""
        try:
            if self.database is None:
                self._connect()
            yield self.database
        except Exception as e:
            logger.error(f"Database operation error: {e}")
            raise
    
    def initialize_database(self):
        """Initialize database and collections with proper indexes"""
        try:
            self._connect()
            self._create_collections_and_indexes()
            self._ensure_user_exists()
            logger.info("MongoDB initialization completed successfully")
            
        except Exception as e:
            logger.error(f"MongoDB initialization failed: {e}")
            raise
    
    def _ensure_user_exists(self):
        """Create database user if it doesn't exist"""
        try:
            admin_db = self.client.admin
            
            # Check if user exists
            users = admin_db.command("usersInfo", self.config.username)
            if not users.get('users'):
                # Create user with readWrite role
                admin_db.command(
                    "createUser",
                    self.config.username,
                    pwd=self.config.password,
                    roles=[
                        {"role": "readWrite", "db": self.config.database},
                        {"role": "dbAdmin", "db": self.config.database}
                    ]
                )
                logger.info(f"User '{self.config.username}' created successfully")
            else:
                logger.info(f"User '{self.config.username}' already exists")
                
        except OperationFailure as e:
            # User might already exist or we might not have permissions
            logger.warning(f"Could not create user (might already exist): {e}")
        except Exception as e:
            logger.error(f"Error ensuring user exists: {e}")
    
    def _create_collections_and_indexes(self):
        """Create collections and indexes for optimal performance"""
        collections_config = {
            'cpu_metrics': {
                'indexes': [
                    [('timestamp', pymongo.DESCENDING)],
                    [('lpar', pymongo.ASCENDING), ('cpu_type', pymongo.ASCENDING)],
                    [('sysplex', pymongo.ASCENDING), ('timestamp', pymongo.DESCENDING)],
                    [('timestamp', pymongo.DESCENDING), ('lpar', pymongo.ASCENDING)]
                ],
                'ttl_field': 'timestamp',
                'ttl_seconds': 7776000  # 90 days
            },
            
            'memory_metrics': {
                'indexes': [
                    [('timestamp', pymongo.DESCENDING)],
                    [('lpar', pymongo.ASCENDING), ('memory_type', pymongo.ASCENDING)],
                    [('sysplex', pymongo.ASCENDING), ('timestamp', pymongo.DESCENDING)]
                ],
                'ttl_field': 'timestamp',
                'ttl_seconds': 7776000
            },
            
            'ldev_utilization_metrics': {
                'indexes': [
                    [('timestamp', pymongo.DESCENDING)],
                    [('device_id', pymongo.ASCENDING)],
                    [('lpar', pymongo.ASCENDING), ('timestamp', pymongo.DESCENDING)]
                ],
                'ttl_field': 'timestamp',
                'ttl_seconds': 7776000
            },
            
            'ldev_response_time_metrics': {
                'indexes': [
                    [('timestamp', pymongo.DESCENDING)],
                    [('device_type', pymongo.ASCENDING)],
                    [('lpar', pymongo.ASCENDING), ('timestamp', pymongo.DESCENDING)]
                ],
                'ttl_field': 'timestamp',
                'ttl_seconds': 7776000
            },
            
            'clpr_service_time_metrics': {
                'indexes': [
                    [('timestamp', pymongo.DESCENDING)],
                    [('cf_link', pymongo.ASCENDING)],
                    [('lpar', pymongo.ASCENDING), ('timestamp', pymongo.DESCENDING)]
                ],
                'ttl_field': 'timestamp',
                'ttl_seconds': 7776000
            },
            
            'clpr_request_rate_metrics': {
                'indexes': [
                    [('timestamp', pymongo.DESCENDING)],
                    [('cf_link', pymongo.ASCENDING), ('request_type', pymongo.ASCENDING)],
                    [('lpar', pymongo.ASCENDING), ('timestamp', pymongo.DESCENDING)]
                ],
                'ttl_field': 'timestamp',
                'ttl_seconds': 7776000
            },
            
            'mpb_processing_rate_metrics': {
                'indexes': [
                    [('timestamp', pymongo.DESCENDING)],
                    [('queue_type', pymongo.ASCENDING)],
                    [('lpar', pymongo.ASCENDING), ('timestamp', pymongo.DESCENDING)]
                ],
                'ttl_field': 'timestamp',
                'ttl_seconds': 7776000
            },
            
            'mpb_queue_depth_metrics': {
                'indexes': [
                    [('timestamp', pymongo.DESCENDING)],
                    [('queue_type', pymongo.ASCENDING)],
                    [('lpar', pymongo.ASCENDING), ('timestamp', pymongo.DESCENDING)]
                ],
                'ttl_field': 'timestamp',
                'ttl_seconds': 7776000
            },
            
            'ports_utilization_metrics': {
                'indexes': [
                    [('timestamp', pymongo.DESCENDING)],
                    [('port_type', pymongo.ASCENDING), ('port_id', pymongo.ASCENDING)],
                    [('lpar', pymongo.ASCENDING), ('timestamp', pymongo.DESCENDING)]
                ],
                'ttl_field': 'timestamp',
                'ttl_seconds': 7776000
            },
            
            'ports_throughput_metrics': {
                'indexes': [
                    [('timestamp', pymongo.DESCENDING)],
                    [('port_type', pymongo.ASCENDING), ('port_id', pymongo.ASCENDING)],
                    [('lpar', pymongo.ASCENDING), ('timestamp', pymongo.DESCENDING)]
                ],
                'ttl_field': 'timestamp',
                'ttl_seconds': 7776000
            },
            
            'volumes_utilization_metrics': {
                'indexes': [
                    [('timestamp', pymongo.DESCENDING)],
                    [('volume_type', pymongo.ASCENDING), ('volume_id', pymongo.ASCENDING)],
                    [('lpar', pymongo.ASCENDING), ('timestamp', pymongo.DESCENDING)]
                ],
                'ttl_field': 'timestamp',
                'ttl_seconds': 7776000
            },
            
            'volumes_iops_metrics': {
                'indexes': [
                    [('timestamp', pymongo.DESCENDING)],
                    [('volume_type', pymongo.ASCENDING), ('volume_id', pymongo.ASCENDING)],
                    [('lpar', pymongo.ASCENDING), ('timestamp', pymongo.DESCENDING)]
                ],
                'ttl_field': 'timestamp',
                'ttl_seconds': 7776000
            }
        }
        
        try:
            for collection_name, config in collections_config.items():
                collection = self.database[collection_name]
                
                # Create indexes
                for index_spec in config['indexes']:
                    try:
                        collection.create_index(index_spec)
                        logger.debug(f"Created index {index_spec} on {collection_name}")
                    except DuplicateKeyError:
                        # Index already exists
                        pass
                
                # Create TTL index for automatic data expiration
                if config.get('ttl_field') and config.get('ttl_seconds'):
                    try:
                        collection.create_index(
                            [(config['ttl_field'], pymongo.ASCENDING)],
                            expireAfterSeconds=config['ttl_seconds']
                        )
                        logger.debug(f"Created TTL index on {collection_name}")
                    except DuplicateKeyError:
                        pass
                
                logger.info(f"Collection '{collection_name}' configured with indexes")
                
        except Exception as e:
            logger.error(f"Error creating collections and indexes: {e}")
            raise
    
    def insert_cpu_metric(self, timestamp: datetime, sysplex: str, lpar: str, 
                         cpu_type: str, utilization_percent: float):
        """Insert CPU utilization metric"""
        try:
            with self.get_database() as db:
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
            with self.get_database() as db:
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
            with self.get_database() as db:
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
            with self.get_database() as db:
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
            with self.get_database() as db:
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
            with self.get_database() as db:
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
            with self.get_database() as db:
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
            with self.get_database() as db:
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
            with self.get_database() as db:
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
            with self.get_database() as db:
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
            with self.get_database() as db:
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
            with self.get_database() as db:
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
    
    def bulk_insert_metrics(self, collection_name: str, documents: List[Dict]):
        """Bulk insert multiple documents for better performance"""
        try:
            with self.get_database() as db:
                collection = db[collection_name]
                result = collection.insert_many(documents, ordered=False)
                logger.debug(f"Bulk inserted {len(result.inserted_ids)} documents to {collection_name}")
                return result.inserted_ids
                
        except Exception as e:
            logger.error(f"Error bulk inserting to {collection_name}: {e}")
            return []
    
    def get_metrics_summary(self, start_time: datetime = None, end_time: datetime = None) -> Dict:
        """Get a summary of metrics for a time range"""
        try:
            with self.get_database() as db:
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
            with self.get_database() as db:
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
            with self.get_database() as db:
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
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data beyond retention period (TTL indexes handle this automatically)"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            with self.get_database() as db:
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
    
    def create_backup(self, backup_path: str = None) -> str:
        """Create a backup of the database"""
        try:
            import subprocess
            from datetime import datetime
            
            if not backup_path:
                backup_path = f"/tmp/rmf_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Use mongodump to create backup
            cmd = [
                'mongodump',
                '--host', f"{self.config.host}:{self.config.port}",
                '--db', self.config.database,
                '--out', backup_path
            ]
            
            if self.config.username:
                cmd.extend(['--username', self.config.username])
                cmd.extend(['--password', self.config.password])
                cmd.extend(['--authenticationDatabase', self.config.auth_source])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Database backup created successfully at {backup_path}")
                return backup_path
            else:
                logger.error(f"Backup failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    def get_connection_status(self) -> Dict:
        """Get connection status and database information"""
        try:
            with self.get_database() as db:
                # Get server status
                server_status = db.command('serverStatus')
                
                # Get database stats
                db_stats = db.command('dbStats')
                
                status = {
                    'connected': True,
                    'server_version': server_status.get('version'),
                    'host': f"{self.config.host}:{self.config.port}",
                    'database': self.config.database,
                    'collections_count': len(db.list_collection_names()),
                    'data_size_mb': round(db_stats.get('dataSize', 0) / (1024 * 1024), 2),
                    'storage_size_mb': round(db_stats.get('storageSize', 0) / (1024 * 1024), 2),
                    'indexes_count': db_stats.get('indexes', 0),
                    'uptime_seconds': server_status.get('uptime')
                }
                
                return status
                
        except Exception as e:
            logger.error(f"Error getting connection status: {e}")
            return {
                'connected': False,
                'error': str(e)
            }
    
    def close_connection(self):
        """Close the database connection"""
        try:
            if self.client:
                self.client.close()
                logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")

# Example usage and testing
if __name__ == "__main__":
    # Initialize the service
    mongo_service = MongoDBService()
    
    # Test connection
    status = mongo_service.get_connection_status()
    print(f"Connection status: {status}")
    
    # Insert sample data
    timestamp = datetime.now()
    mongo_service.insert_cpu_metric(timestamp, "SYSPLEX01", "PROD01", "general_purpose", 75.5)
    mongo_service.insert_memory_metric(timestamp, "SYSPLEX01", "PROD01", "real_storage", 1073741824)
    
    # Get summary
    summary = mongo_service.get_metrics_summary()
    print(f"Metrics summary: {summary}")
    
    # Close connection
    mongo_service.close_connection()