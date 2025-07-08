import os
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Database configuration with environment variable defaults"""
    host: str = os.getenv('MYSQL_HOST', 'localhost')
    port: int = int(os.getenv('MYSQL_PORT', '3306'))
    database: str = os.getenv('MYSQL_DATABASE', 'rmf_monitoring')
    user: str = os.getenv('MYSQL_USER', 'rmf_user')
    password: str = os.getenv('MYSQL_PASSWORD', 'rmf_password')
    root_password: str = os.getenv('MYSQL_ROOT_PASSWORD', 'root_password')
    
    def get_connection_params(self) -> dict:
        """Get connection parameters as dictionary"""
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password,
            'autocommit': True
        }
    
    def get_root_connection_params(self) -> dict:
        """Get root connection parameters as dictionary"""
        return {
            'host': self.host,
            'port': self.port,
            'user': 'root',
            'password': self.root_password,
            'autocommit': True
        }