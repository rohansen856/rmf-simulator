from mysql.connector import Error
from utils.logger import logger
from .connection import DatabaseConnection
from .schema import TABLES
from .config import DatabaseConfig

class DatabaseInitializer:
    """Handles database and table initialization"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self.connection_manager = DatabaseConnection(config)
    
    def initialize_database(self):
        """Initialize database, user, and tables if they don't exist"""
        try:
            # Create database and user if they don't exist
            # self._create_database_and_user()
            
            # Create tables
            self._create_tables()
            
            logger.info("Database initialization completed successfully")
            
        except Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _create_database_and_user(self):
        """Create database and user if they don't exist"""
        try:
            connection = self.connection_manager._get_root_connection()
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
            
            connection.close()
            
        except Error as e:
            logger.error(f"Error creating database and user: {e}")
            raise
    
    def _create_tables(self):
        """Create all required tables"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor()
                
                for table_name, table_sql in TABLES.items():
                    cursor.execute(table_sql)
                    logger.info(f"Table '{table_name}' created or already exists")
                    
        except Error as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def drop_all_tables(self):
        """Drop all tables (use with caution)"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor()
                
                for table_name in TABLES.keys():
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                    logger.info(f"Table '{table_name}' dropped")
                    
        except Error as e:
            logger.error(f"Error dropping tables: {e}")
            raise