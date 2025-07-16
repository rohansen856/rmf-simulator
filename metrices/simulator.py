import os
from datetime import datetime
from typing import List, Optional

from models.lpar import LPARConfig
from metrices.simulators.factory import SimulatorFactory
from storage.storage_manager import StorageManager
from utils.logger import logger
from utils.confiig import LPAR_CONFIGS


class MainframeSimulator:
    """Main orchestrator for mainframe metrics simulation"""
    
    def __init__(self, 
            sysplex_name: str = "SYSPLEX01",
            enable_mysql: bool = True, 
            enable_mongodb: bool = True, 
            enable_s3: bool = True,
            enabled_simulators: Optional[List[str]] = None
        ):
        
        self.sysplex_name = sysplex_name
        self.start_time = datetime.now()
        
        # Initialize storage manager
        self.storage_manager = StorageManager(
            enable_mysql=enable_mysql,
            enable_mongodb=enable_mongodb,
            enable_s3=enable_s3
        )
        
        # Initialize simulator factory
        self.simulator_factory = SimulatorFactory(sysplex_name)
        
        # Create enabled simulators
        self.enabled_simulators = enabled_simulators or ['cpu', 'memory', 'storage', 'network', 'clpr', 'mpb', 'volumes']
        self.simulators = {}
        
        self._initialize_simulators()
        logger.info(f"MainframeSimulator initialized for {sysplex_name}")
    
    def _initialize_simulators(self):
        """Initialize the requested simulators"""
        for simulator_type in self.enabled_simulators:
            try:
                self.simulators[simulator_type] = self.simulator_factory.create_simulator(simulator_type)
                logger.info(f"Initialized {simulator_type} simulator")
            except Exception as e:
                logger.error(f"Failed to initialize {simulator_type} simulator: {e}")
    
    def add_simulator(self, simulator_type: str):
        """Add a new simulator type"""
        if simulator_type not in self.simulators:
            try:
                self.simulators[simulator_type] = self.simulator_factory.create_simulator(simulator_type)
                if simulator_type not in self.enabled_simulators:
                    self.enabled_simulators.append(simulator_type)
                logger.info(f"Added {simulator_type} simulator")
            except Exception as e:
                logger.error(f"Failed to add {simulator_type} simulator: {e}")
    
    def remove_simulator(self, simulator_type: str):
        """Remove a simulator type"""
        if simulator_type in self.simulators:
            del self.simulators[simulator_type]
            if simulator_type in self.enabled_simulators:
                self.enabled_simulators.remove(simulator_type)
            logger.info(f"Removed {simulator_type} simulator")
    
    def simulate_lpar_metrics(self, lpar_config: LPARConfig):
        """Generate metrics for a single LPAR"""
        all_metrics = []
        
        for simulator_type, simulator in self.simulators.items():
            try:
                metrics = simulator.simulate(lpar_config)
                all_metrics.extend(metrics)
                logger.debug(f"Generated {len(metrics)} {simulator_type} metrics for {lpar_config.name}")
            except Exception as e:
                logger.error(f"Error generating {simulator_type} metrics for {lpar_config.name}: {e}")
        
        # Store all metrics
        if all_metrics:
            try:
                self.storage_manager.store_metrics(all_metrics)
                logger.debug(f"Stored {len(all_metrics)} metrics for {lpar_config.name}")
            except Exception as e:
                logger.error(f"Error storing metrics for {lpar_config.name}: {e}")
        
        return all_metrics
    
    async def update_all_metrics(self):
        """Update metrics for all LPARs"""
        total_metrics = 0
        
        for lpar_config in LPAR_CONFIGS:
            try:
                metrics = self.simulate_lpar_metrics(lpar_config)
                total_metrics += len(metrics)
                logger.debug(f"Updated metrics for {lpar_config.name}")
            except Exception as e:
                logger.error(f"Error updating metrics for {lpar_config.name}: {e}")
        
        # Force flush storage after each complete update cycle
        try:
            self.storage_manager.force_flush()
            logger.debug(f"Generated and stored {total_metrics} total metrics")
        except Exception as e:
            logger.error(f"Error flushing storage: {e}")
    
    def get_simulator_status(self) -> dict:
        """Get status of all simulators"""
        return {
            'sysplex_name': self.sysplex_name,
            'start_time': self.start_time.isoformat(),
            'enabled_simulators': self.enabled_simulators,
            'available_simulators': self.simulator_factory.get_available_types(),
            'storage_backends': {
                'mysql': self.storage_manager.db_service is not None,
                'mongodb': self.storage_manager.mongo_service is not None,
                's3': self.storage_manager.s3_service is not None
            }
        }
    
    def close(self):
        """Clean up resources"""
        try:
            self.storage_manager.close()
            logger.info("MainframeSimulator closed successfully")
        except Exception as e:
            logger.error(f"Error closing MainframeSimulator: {e}")


# Factory function for easy initialization
def create_simulator_from_env() -> MainframeSimulator:
    """Create simulator instance from environment variables"""
    return MainframeSimulator(
        enable_mysql=os.getenv("ENABLE_MYSQL", "true").lower() == "true",
        enable_mongodb=os.getenv("ENABLE_MONGO", "true").lower() == "true", 
        enable_s3=os.getenv("ENABLE_S3", "true").lower() == "true",
        enabled_simulators=os.getenv("ENABLED_SIMULATORS", "cpu,memory,storage,network,clpr,mpb,volumes").split(",")
    )


# Initialize default simulator instance
simulator = create_simulator_from_env()