import random
from datetime import datetime
from typing import Dict, Any, List

from metrices.definitions import PORTS_UTILIZATION, PORTS_THROUGHPUT
from models.lpar import LPARConfig
from metrices.simulators.base import BaseMetricSimulator
from utils.logger import logger


class NetworkMetricSimulator(BaseMetricSimulator):
    """Simulator for network port metrics"""
    
    def __init__(self, sysplex_name: str):
        super().__init__(sysplex_name)
        self.port_types = {
            "OSA": {"count": 4, "max_throughput": 1000, "base_util": 35.0},
            "Hipersocket": {"count": 2, "max_throughput": 10000, "base_util": 15.0},
            "FICON": {"count": 8, "max_throughput": 400, "base_util": 45.0},
        }
    
    def simulate(self, lpar_config: LPARConfig) -> List[Dict[str, Any]]:
        """Generate network port metrics for an LPAR"""
        self.initialize_baseline(lpar_config)
        
        time_factor = self.get_time_factor(lpar_config)
        timestamp = datetime.now()
        metrics = []
        
        for port_type, config in self.port_types.items():
            for i in range(config["count"]):
                port_id = f"{port_type}_{i:02d}"
                
                # Utilization
                utilization = config["base_util"] * time_factor * (1 + random.uniform(-0.4, 0.6))
                utilization = max(5.0, min(85.0, utilization))
                
                # Throughput
                throughput = config["max_throughput"] * (utilization / 100.0)
                throughput = max(1.0, throughput)
                
                # Update Prometheus metrics
                PORTS_UTILIZATION.labels(
                    sysplex=self.sysplex_name,
                    lpar=lpar_config.name,
                    port_type=port_type,
                    port_id=port_id
                ).set(utilization)
                
                PORTS_THROUGHPUT.labels(
                    sysplex=self.sysplex_name,
                    lpar=lpar_config.name,
                    port_type=port_type,
                    port_id=port_id
                ).set(throughput)
                
                # Prepare metrics for storage
                metrics.extend([
                    {
                        'timestamp': timestamp.isoformat(),
                        'sysplex': self.sysplex_name,
                        'lpar': lpar_config.name,
                        'port_type': port_type,
                        'port_id': port_id,
                        'utilization_percent': utilization,
                        'metric_type': 'ports_utilization'
                    },
                    {
                        'timestamp': timestamp.isoformat(),
                        'sysplex': self.sysplex_name,
                        'lpar': lpar_config.name,
                        'port_type': port_type,
                        'port_id': port_id,
                        'throughput_mbps': throughput,
                        'metric_type': 'ports_throughput'
                    }
                ])
        
        logger.debug(f"Network metrics updated for {lpar_config.name}: {len(metrics)} metrics generated")
        return metrics
    
    def get_metric_type(self) -> str:
        return "network_metrics"