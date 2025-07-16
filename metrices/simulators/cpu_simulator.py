from datetime import datetime
from typing import Dict, Any, List

from metrices.definitions import CPU_UTILIZATION
from models.lpar import LPARConfig
from metrices.simulators.base import BaseMetricSimulator
from utils.logger import logger


class CPUMetricSimulator(BaseMetricSimulator):
    """Simulator for CPU utilization metrics"""
    
    def __init__(self, sysplex_name: str):
        super().__init__(sysplex_name)
        self.cpu_types = ["general_purpose", "ziip", "zaap"]
    
    def simulate(self, lpar_config: LPARConfig) -> List[Dict[str, Any]]:
        """Generate CPU metrics for an LPAR"""
        self.initialize_baseline(lpar_config)
        
        time_factor = self.get_time_factor(lpar_config)
        base_util = self.base_values[lpar_config.name]['cpu_base']
        timestamp = datetime.now()
        
        # General purpose CPU utilization
        gp_util = min(95.0, base_util * time_factor)
        
        # Specialty engine utilization (zIIP/zAAP)
        ziip_util = min(75.0, gp_util * 0.6)
        zaap_util = min(70.0, gp_util * 0.4)
        
        cpu_values = {
            "general_purpose": gp_util,
            "ziip": ziip_util,
            "zaap": zaap_util
        }
        
        # Update Prometheus metrics
        for cpu_type, utilization in cpu_values.items():
            CPU_UTILIZATION.labels(
                sysplex=self.sysplex_name,
                lpar=lpar_config.name,
                cpu_type=cpu_type
            ).set(utilization)
        
        # Prepare metrics for storage
        metrics = []
        for cpu_type, utilization in cpu_values.items():
            metrics.append({
                'timestamp': timestamp.isoformat(),
                'sysplex': self.sysplex_name,
                'lpar': lpar_config.name,
                'cpu_type': cpu_type,
                'utilization_percent': utilization,
                'metric_type': self.get_metric_type()
            })
        
        logger.debug(f"CPU metrics updated for {lpar_config.name}: GP={gp_util:.1f}%, zIIP={ziip_util:.1f}%")
        return metrics
    
    def get_metric_type(self) -> str:
        return "cpu_utilization"