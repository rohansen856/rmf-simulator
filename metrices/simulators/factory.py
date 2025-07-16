from typing import Dict, List, Type
from metrices.simulators.base import BaseMetricSimulator
from metrices.simulators.cpu_simulator import CPUMetricSimulator
from metrices.simulators.memory_simulator import MemoryMetricSimulator
from metrices.simulators.storage_simulator import StorageMetricSimulator
from metrices.simulators.network_simulator import NetworkMetricSimulator
from metrices.simulators.clpr_simulator import CLPRMetricSimulator
from metrices.simulators.mpb_simulator import MPBMetricSimulator
from metrices.simulators.volumes_simulator import VolumesMetricSimulator
from utils.logger import logger


class SimulatorFactory:
    """Factory for creating and managing metric simulators"""
    
    def __init__(self, sysplex_name: str):
        self.sysplex_name = sysplex_name
        self._simulators: Dict[str, BaseMetricSimulator] = {}
        self._available_simulators = {
            'cpu': CPUMetricSimulator,
            'memory': MemoryMetricSimulator,
            'storage': StorageMetricSimulator,
            'network': NetworkMetricSimulator,
            'clpr': CLPRMetricSimulator,
            'mpb': MPBMetricSimulator,
            'volumes': VolumesMetricSimulator,
        }
    
    def create_simulator(self, simulator_type: str) -> BaseMetricSimulator:
        """Create a simulator instance"""
        if simulator_type not in self._available_simulators:
            raise ValueError(f"Unknown simulator type: {simulator_type}")
        
        if simulator_type not in self._simulators:
            simulator_class = self._available_simulators[simulator_type]
            self._simulators[simulator_type] = simulator_class(self.sysplex_name)
            logger.info(f"Created {simulator_type} simulator")
        
        return self._simulators[simulator_type]
    
    def get_simulator(self, simulator_type: str) -> BaseMetricSimulator:
        """Get an existing simulator instance"""
        if simulator_type not in self._simulators:
            return self.create_simulator(simulator_type)
        return self._simulators[simulator_type]
    
    def get_all_simulators(self) -> Dict[str, BaseMetricSimulator]:
        """Get all simulator instances, creating them if necessary"""
        for simulator_type in self._available_simulators:
            if simulator_type not in self._simulators:
                self.create_simulator(simulator_type)
        return self._simulators.copy()
    
    def register_simulator(self, name: str, simulator_class: Type[BaseMetricSimulator]):
        """Register a new simulator type"""
        self._available_simulators[name] = simulator_class
        logger.info(f"Registered custom simulator: {name}")
    
    def get_available_types(self) -> List[str]:
        """Get list of available simulator types"""
        return list(self._available_simulators.keys())