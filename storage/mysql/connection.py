import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from utils.logger import logger
from .config import DatabaseConfig

class DatabaseConnection:
    """Handles database connections and connection management"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
    
    def _get_root_connection(self):
        """Get connection as root to create database and user"""
        try:
            connection = mysql.connector.connect(
                **self.config.get_root_connection_params()
            )
            return connection
        except Error as e:
            logger.error(f"Error connecting to MySQL as root: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get a database connection with automatic cleanup"""
        connection = None
        try:
            connection = mysql.connector.connect(
                **self.config.get_connection_params()
            )
            yield connection
        except Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def test_connection(self) -> bool:
        """Test if database connection is working"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
        except Error as e:
            logger.error(f"Connection test failed: {e}")
            return False