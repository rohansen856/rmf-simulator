import random
from datetime import datetime
from typing import Dict, Any, List

from metrices.definitions import MEMORY_USAGE
from models.lpar import LPARConfig
from metrices.simulators.base import BaseMetricSimulator
from utils.logger import logger


class MemoryMetricSimulator(BaseMetricSimulator):
    """Simulator for memory usage metrics"""
    
    def __init__(self, sysplex_name: str):
        super().__init__(sysplex_name)
        self.memory_types = ["real_storage", "virtual_storage", "csa"]
    
    def simulate(self, lpar_config: LPARConfig) -> List[Dict[str, Any]]:
        """Generate memory metrics for an LPAR"""
        self.initialize_baseline(lpar_config)
        
        time_factor = self.get_time_factor(lpar_config)
        base_util = self.base_values[lpar_config.name]['memory_base']
        timestamp = datetime.now()
        
        # Calculate memory usage
        memory_util = min(0.90, base_util * time_factor)
        total_memory = lpar_config.memory_gb * 1024 * 1024 * 1024  # Convert to bytes
        used_memory = int(total_memory * memory_util)
        
        # Virtual storage (typically 3-10x real storage)
        virtual_multiplier = 4.0 if lpar_config.workload_type == "online" else 6.0
        virtual_memory = int(total_memory * virtual_multiplier)
        
        # Common Service Area (CSA)
        csa_memory = random.randint(200_000_000, 800_000_000)  # 200-800MB
        
        memory_values = {
            "real_storage": used_memory,
            "virtual_storage": virtual_memory,
            "csa": csa_memory
        }
        
        # Update Prometheus metrics
        for memory_type, usage in memory_values.items():
            MEMORY_USAGE.labels(
                sysplex=self.sysplex_name,
                lpar=lpar_config.name,
                memory_type=memory_type
            ).set(usage)
        
        # Prepare metrics for storage
        metrics = []
        for memory_type, usage in memory_values.items():
            metrics.append({
                'timestamp': timestamp.isoformat(),
                'sysplex': self.sysplex_name,
                'lpar': lpar_config.name,
                'memory_type': memory_type,
                'usage_bytes': usage,
                'metric_type': self.get_metric_type()
            })
        
        logger.debug(f"Memory metrics updated for {lpar_config.name}: Real={used_memory//1024//1024}MB")
        return metrics
    
    def get_metric_type(self) -> str:
        return "memory_usage"