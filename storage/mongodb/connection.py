"""
MongoDB Connection Manager
"""
from contextlib import contextmanager
from typing import Optional

import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

from .config import MongoConfig
from utils.logger import logger


class MongoConnectionManager:
    """Manages MongoDB connections and database operations"""
    
    def __init__(self, config: Optional[MongoConfig] = None):
        self.config = config or MongoConfig()
        self.client: Optional[MongoClient] = None
        self.database = None
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            connection_string = self.config.get_connection_string()
            self.client = MongoClient(
                connection_string,
                authSource=self.config.auth_source,
                connectTimeoutMS=self.config.connection_timeout,
                serverSelectionTimeoutMS=self.config.server_selection_timeout,
                maxPoolSize=self.config.max_pool_size,
                minPoolSize=self.config.min_pool_size,
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
                self.connect()
            yield self.database
        except Exception as e:
            logger.error(f"Database operation error: {e}")
            raise
    
    def ensure_user_exists(self):
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
    
    def get_connection_status(self) -> dict:
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