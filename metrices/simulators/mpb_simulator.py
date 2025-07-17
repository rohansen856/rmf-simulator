import random
from datetime import datetime
from typing import Dict, Any, List

from metrices.definitions import MPB_PROCESSING_RATE, MPB_QUEUE_DEPTH
from models.lpar import LPARConfig
from metrices.simulators.base import BaseMetricSimulator
from utils.logger import logger


class MPBMetricSimulator(BaseMetricSimulator):
    """Simulator for Message Processing Block metrics"""
    
    def __init__(self, sysplex_name: str):
        super().__init__(sysplex_name)
        self.queue_types = ["CICS", "IMS", "MQ", "BATCH"]
        self.base_rates = {
            "CICS": 5000,
            "IMS": 3000,
            "MQ": 2000,
            "BATCH": 500
        }
    
    def simulate(self, lpar_config: LPARConfig) -> List[Dict[str, Any]]:
        """Generate MPB metrics for an LPAR"""
        self.initialize_baseline(lpar_config)
        
        time_factor = self.get_time_factor(lpar_config)
        timestamp = datetime.now()
        metrics = []
        
        for queue_type in self.queue_types:
            # Processing rate varies by queue type and workload
            base_rate = self.base_rates.get(queue_type, 1000)
            
            processing_rate = base_rate * time_factor * (1 + random.uniform(-0.2, 0.3))
            processing_rate = max(100, processing_rate)
            
            # Queue depth increases with load
            queue_depth = max(1, int(processing_rate / 1000 * random.uniform(0.1, 0.5)))
            
            # Update Prometheus metrics
            MPB_PROCESSING_RATE.labels(
                sysplex=self.sysplex_name,
                lpar=lpar_config.name,
                queue_type=queue_type
            ).set(processing_rate)
            
            MPB_QUEUE_DEPTH.labels(
                sysplex=self.sysplex_name,
                lpar=lpar_config.name,
                queue_type=queue_type
            ).set(queue_depth)
            
            # Prepare metrics for storage
            metrics.extend([
                {
                    'timestamp': timestamp.isoformat(),
                    'sysplex': self.sysplex_name,
                    'lpar': lpar_config.name,
                    'queue_type': queue_type,
                    'processing_rate': processing_rate,
                    'metric_type': 'mpb_processing_rate'
                },
                {
                    'timestamp': timestamp.isoformat(),
                    'sysplex': self.sysplex_name,
                    'lpar': lpar_config.name,
                    'queue_type': queue_type,
                    'queue_depth': queue_depth,
                    'metric_type': 'mpb_queue_depth'
                }
            ])
        
        logger.debug(f"MPB metrics updated for {lpar_config.name}: {len(metrics)} metrics generated")
        return metrics
    
    def get_metric_type(self) -> str:
        return "mpb_metrics"