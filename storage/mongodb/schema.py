"""
MongoDB Schema and Collections Setup
"""
import pymongo
from pymongo.errors import DuplicateKeyError

from utils.logger import logger


class MongoSchemaManager:
    """Manages MongoDB collections, indexes, and schema setup"""
    
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
    
    @property
    def collections_config(self):
        """Define collections configuration with indexes and TTL settings"""
        return {
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
    
    def create_collections_and_indexes(self):
        """Create collections and indexes for optimal performance"""
        try:
            with self.connection_manager.get_database() as database:
                for collection_name, config in self.collections_config.items():
                    collection = database[collection_name]
                    
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
    
    def initialize_schema(self):
        """Initialize database schema"""
        try:
            self.connection_manager.connect()
            self.create_collections_and_indexes()
            self.connection_manager.ensure_user_exists()
            logger.info("MongoDB schema initialization completed successfully")
            
        except Exception as e:
            logger.error(f"MongoDB schema initialization failed: {e}")
            raise
    
    def get_collection_names(self):
        """Get list of all collection names"""
        return list(self.collections_config.keys())