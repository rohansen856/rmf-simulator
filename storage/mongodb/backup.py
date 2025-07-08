"""
MongoDB Backup Operations
"""
import subprocess
from datetime import datetime
from typing import Optional

from utils.logger import logger


class MongoBackupManager:
    """Handles MongoDB backup and restore operations"""
    
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
    
    def create_backup(self, backup_path: str = None) -> Optional[str]:
        """Create a backup of the database"""
        try:
            if not backup_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"/tmp/rmf_backup_{timestamp}"
            
            config = self.connection_manager.config
            
            # Use mongodump to create backup
            cmd = [
                'mongodump',
                '--host', f"{config.host}:{config.port}",
                '--db', config.database,
                '--out', backup_path
            ]
            
            if config.username:
                cmd.extend(['--username', config.username])
                cmd.extend(['--password', config.password])
                cmd.extend(['--authenticationDatabase', config.auth_source])
            
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
    
    def restore_backup(self, backup_path: str, drop_existing: bool = False) -> bool:
        """Restore database from backup"""
        try:
            config = self.connection_manager.config
            
            # Use mongorestore to restore backup
            cmd = [
                'mongorestore',
                '--host', f"{config.host}:{config.port}",
                '--db', config.database,
                backup_path
            ]
            
            if drop_existing:
                cmd.append('--drop')
            
            if config.username:
                cmd.extend(['--username', config.username])
                cmd.extend(['--password', config.password])
                cmd.extend(['--authenticationDatabase', config.auth_source])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Database restored successfully from {backup_path}")
                return True
            else:
                logger.error(f"Restore failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False
    
    def export_collection_to_json(self, collection_name: str, output_path: str,
                                 query_filter: dict = None) -> bool:
        """Export a collection to JSON file"""
        try:
            config = self.connection_manager.config
            
            cmd = [
                'mongoexport',
                '--host', f"{config.host}:{config.port}",
                '--db', config.database,
                '--collection', collection_name,
                '--out', output_path,
                '--jsonArray'
            ]
            
            if query_filter:
                import json
                cmd.extend(['--query', json.dumps(query_filter)])
            
            if config.username:
                cmd.extend(['--username', config.username])
                cmd.extend(['--password', config.password])
                cmd.extend(['--authenticationDatabase', config.auth_source])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Collection {collection_name} exported to {output_path}")
                return True
            else:
                logger.error(f"Export failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error exporting collection: {e}")
            return False
    
    def import_collection_from_json(self, collection_name: str, input_path: str,
                                   drop_existing: bool = False) -> bool:
        """Import a collection from JSON file"""
        try:
            config = self.connection_manager.config
            
            cmd = [
                'mongoimport',
                '--host', f"{config.host}:{config.port}",
                '--db', config.database,
                '--collection', collection_name,
                '--file', input_path,
                '--jsonArray'
            ]
            
            if drop_existing:
                cmd.append('--drop')
            
            if config.username:
                cmd.extend(['--username', config.username])
                cmd.extend(['--password', config.password])
                cmd.extend(['--authenticationDatabase', config.auth_source])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Collection {collection_name} imported from {input_path}")
                return True
            else:
                logger.error(f"Import failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error importing collection: {e}")
            return False