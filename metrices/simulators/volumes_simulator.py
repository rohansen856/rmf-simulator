import random
from datetime import datetime
from typing import Dict, Any, List

from metrices.definitions import VOLUMES_UTILIZATION, VOLUMES_IOPS
from models.lpar import LPARConfig
from metrices.simulators.base import BaseMetricSimulator
from utils.logger import logger


class VolumesMetricSimulator(BaseMetricSimulator):
    """Simulator for volume utilization and IOPS metrics"""
    
    def __init__(self, sysplex_name: str):
        super().__init__(sysplex_name)
        self.volume_types = {
            "SYSRES": {"count": 2, "base_util": 60.0, "base_iops": 1500},
            "WORK": {"count": 15, "base_util": 45.0, "base_iops": 800},
            "USER": {"count": 25, "base_util": 35.0, "base_iops": 600},
            "TEMP": {"count": 8, "base_util": 25.0, "base_iops": 400},
        }
    
    def simulate(self, lpar_config: LPARConfig) -> List[Dict[str, Any]]:
        """Generate volume metrics for an LPAR"""
        self.initialize_baseline(lpar_config)
        
        time_factor = self.get_time_factor(lpar_config)
        timestamp = datetime.now()
        metrics = []
        
        for volume_type, config in self.volume_types.items():
            for i in range(config["count"]):
                volume_id = f"{volume_type}{i:03d}"
                
                # Utilization
                utilization = config["base_util"] * time_factor * (1 + random.uniform(-0.3, 0.4))
                utilization = max(10.0, min(90.0, utilization))
                
                # IOPS
                iops = config["base_iops"] * time_factor * (1 + random.uniform(-0.4, 0.6))
                iops = max(50, int(iops))
                
                # Update Prometheus metrics
                VOLUMES_UTILIZATION.labels(
                    sysplex=self.sysplex_name,
                    lpar=lpar_config.name,
                    volume_type=volume_type,
                    volume_id=volume_id
                ).set(utilization)
                
                VOLUMES_IOPS.labels(
                    sysplex=self.sysplex_name,
                    lpar=lpar_config.name,
                    volume_type=volume_type,
                    volume_id=volume_id
                ).set(iops)
                
                # Prepare metrics for storage
                metrics.extend([
                    {
                        'timestamp': timestamp.isoformat(),
                        'sysplex': self.sysplex_name,
                        'lpar': lpar_config.name,
                        'volume_type': volume_type,
                        'volume_id': volume_id,
                        'utilization_percent': utilization,
                        'metric_type': 'volumes_utilization'
                    },
                    {
                        'timestamp': timestamp.isoformat(),
                        'sysplex': self.sysplex_name,
                        'lpar': lpar_config.name,
                        'volume_type': volume_type,
                        'volume_id': volume_id,
                        'iops': iops,
                        'metric_type': 'volumes_iops'
                    }
                ])
        
        logger.debug(f"Volumes metrics updated for {lpar_config.name}: {len(metrics)} metrics generated")
        return metrics
    
    def get_metric_type(self) -> str:
        return "volumes_metrics"