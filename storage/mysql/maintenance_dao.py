from datetime import datetime
from mysql.connector import Error
from utils.logger import logger
from .connection import DatabaseConnection
from .config import DatabaseConfig
from .schema import TABLE_NAMES

class MaintenanceDAO:
    """Data Access Object for maintenance operations"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.connection_manager = DatabaseConnection(config)
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data beyond retention period"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor()
                
                total_deleted = 0
                for table in TABLE_NAMES:
                    query = f"""
                        DELETE FROM {table} 
                        WHERE timestamp < DATE_SUB(NOW(), INTERVAL %s DAY)
                    """
                    cursor.execute(query, (days_to_keep,))
                    deleted_count = cursor.rowcount
                    total_deleted += deleted_count
                    logger.info(f"Cleaned up {deleted_count} old records from {table}")
                
                logger.info(f"Total records cleaned up: {total_deleted}")
                return total_deleted
                    
        except Error as e:
            logger.error(f"Error cleaning up old data: {e}")
            raise
    
    def vacuum_tables(self):
        """Optimize all tables for better performance"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor()
                
                for table in TABLE_NAMES:
                    cursor.execute(f"OPTIMIZE TABLE {table}")
                    logger.info(f"Optimized table {table}")
                
                logger.info("All tables optimized successfully")
                
        except Error as e:
            logger.error(f"Error optimizing tables: {e}")
            raise
    
    def get_table_sizes(self) -> dict:
        """Get size information for all tables"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                query = """
                    SELECT 
                        table_name,
                        table_rows,
                        data_length,
                        index_length,
                        (data_length + index_length) as total_size
                    FROM information_schema.tables
                    WHERE table_schema = %s
                    ORDER BY total_size DESC
                """
                cursor.execute(query, (self.connection_manager.config.database,))
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error getting table sizes: {e}")
            return {}
    
    def analyze_table_statistics(self, table_name: str) -> dict:
        """Get detailed statistics for a specific table"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                # Get basic table info
                cursor.execute(f"SELECT COUNT(*) as total_rows FROM {table_name}")
                row_count = cursor.fetchone()['total_rows']
                
                # Get timestamp range
                cursor.execute(f"""
                    SELECT 
                        MIN(timestamp) as earliest_record,
                        MAX(timestamp) as latest_record
                    FROM {table_name}
                """)
                time_range = cursor.fetchone()
                
                # Get daily record counts for the last 30 days
                cursor.execute(f"""
                    SELECT 
                        DATE(timestamp) as date,
                        COUNT(*) as records
                    FROM {table_name}
                    WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                """)
                daily_counts = cursor.fetchall()
                
                return {
                    'table_name': table_name,
                    'total_rows': row_count,
                    'earliest_record': time_range['earliest_record'],
                    'latest_record': time_range['latest_record'],
                    'daily_counts_last_30_days': daily_counts
                }
                
        except Error as e:
            logger.error(f"Error analyzing table statistics for {table_name}: {e}")
            return {}
    
    def backup_table(self, table_name: str, backup_file: str):
        """Create a backup of a specific table (requires mysqldump)"""
        import subprocess
        import os
        
        try:
            config = self.connection_manager.config
            
            # Build mysqldump command
            cmd = [
                'mysqldump',
                f'--host={config.host}',
                f'--port={config.port}',
                f'--user={config.user}',
                f'--password={config.password}',
                config.database,
                table_name
            ]
            
            # Execute backup
            with open(backup_file, 'w') as f:
                subprocess.run(cmd, stdout=f, check=True)
            
            logger.info(f"Table {table_name} backed up to {backup_file}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error backing up table {table_name}: {e}")
            raise
        except FileNotFoundError:
            logger.error("mysqldump not found. Please install MySQL client tools.")
            raise
    
    def truncate_table(self, table_name: str):
        """Truncate a specific table (removes all data)"""
        try:
            with self.connection_manager.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(f"TRUNCATE TABLE {table_name}")
                logger.info(f"Table {table_name} truncated successfully")
                
        except Error as e:
            logger.error(f"Error truncating table {table_name}: {e}")
            raise