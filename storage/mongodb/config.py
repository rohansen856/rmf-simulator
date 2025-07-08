"""
MongoDB Configuration Module
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class MongoConfig:
    """MongoDB configuration settings"""
    host: str = os.getenv('MONGO_HOST', 'localhost')
    port: int = int(os.getenv('MONGO_PORT', '27017'))
    database: str = os.getenv('MONGO_DATABASE', 'rmf_monitoring')
    username: str = os.getenv('MONGO_USERNAME', 'rmf_user')
    password: str = os.getenv('MONGO_PASSWORD', 'rmf_password')
    auth_source: str = os.getenv('MONGO_AUTH_SOURCE', 'admin')
    replica_set: Optional[str] = os.getenv('MONGO_REPLICA_SET', None)
    connection_timeout: int = int(os.getenv('MONGO_CONNECTION_TIMEOUT', '5000'))
    server_selection_timeout: int = int(os.getenv('MONGO_SERVER_SELECTION_TIMEOUT', '5000'))
    max_pool_size: int = int(os.getenv('MONGO_MAX_POOL_SIZE', '50'))
    min_pool_size: int = int(os.getenv('MONGO_MIN_POOL_SIZE', '5'))
    
    def get_connection_string(self) -> str:
        """Build MongoDB connection string"""
        if self.username and self.password:
            auth_part = f"{self.username}:{self.password}@"
        else:
            auth_part = ""
        
        if self.replica_set:
            replica_part = f"?replicaSet={self.replica_set}"
        else:
            replica_part = ""
        
        return f"mongodb://{auth_part}{self.host}:{self.port}/{self.database}{replica_part}"