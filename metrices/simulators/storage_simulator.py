import random
from datetime import datetime
from typing import Dict, Any, List

from metrices.definitions import LDEV_RESPONSE_TIME, LDEV_UTILIZATION
from models.lpar import LPARConfig
from metrices.simulators.base import BaseMetricSimulator
from utils.logger import logger


class StorageMetricSimulator(BaseMetricSimulator):
    """Simulator for LDEV (storage device) metrics"""
    
    def __init__(self, sysplex_name: str):
        super().__init__(sysplex_name)
        self.device_types = {
            "3390": {"count": 20, "response_base": 8.0, "util_base": 40.0},
            "flashcopy": {"count": 8, "response_base": 2.0, "util_base": 55.0},
            "tape": {"count": 12, "response_base": 45.0, "util_base": 25.0},
        }
    
    def simulate(self, lpar_config: LPARConfig) -> List[Dict[str, Any]]:
        """Generate LDEV metrics for an LPAR"""
        self.initialize_baseline(lpar_config)
        
        time_factor = self.get_time_factor(lpar_config)
        timestamp = datetime.now()
        metrics = []
        
        for device_type, config in self.device_types.items():
            for i in range(config["count"]):
                device_id = f"{device_type}_{i:02d}"
                
                # Response time calculation
                response_time = config["response_base"] * time_factor * (1 + random.uniform(-0.2, 0.3))
                response_time = max(1.0, min(100.0, response_time))  # Clamp between 1-100ms
                
                # Utilization calculation
                utilization = config["util_base"] * time_factor * (1 + random.uniform(-0.3, 0.4))
                utilization = max(5.0, min(95.0, utilization))  # Clamp between 5-95%
                
                # Update Prometheus metrics
                LDEV_RESPONSE_TIME.labels(
                    sysplex=self.sysplex_name,
                    lpar=lpar_config.name,
                    device_type=device_type
                ).observe(response_time / 1000.0)  # Convert to seconds
                
                LDEV_UTILIZATION.labels(
                    sysplex=self.sysplex_name,
                    lpar=lpar_config.name,
                    device_id=device_id
                ).set(utilization)
                
                # Prepare metrics for storage
                metrics.extend([
                    {
                        'timestamp': timestamp.isoformat(),
                        'sysplex': self.sysplex_name,
                        'lpar': lpar_config.name,
                        'device_type': device_type,
                        'response_time_seconds': response_time / 1000.0,
                        'metric_type': 'ldev_response_time'
                    },
                    {
                        'timestamp': timestamp.isoformat(),
                        'sysplex': self.sysplex_name,
                        'lpar': lpar_config.name,
                        'device_id': device_id,
                        'utilization_percent': utilization,
                        'metric_type': 'ldev_utilization'
                    }
                ])
        
        logger.debug(f"Storage metrics updated for {lpar_config.name}: {len(metrics)} metrics generated")
        return metrics
    
    def get_metric_type(self) -> str:
        return "storage_metrics"