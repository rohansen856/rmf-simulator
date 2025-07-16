import random
from datetime import datetime
from typing import Dict, Any, List

from metrices.definitions import CLPR_SERVICE_TIME, CLPR_REQUEST_RATE
from models.lpar import LPARConfig
from metrices.simulators.base import BaseMetricSimulator
from utils.logger import logger


class CLPRMetricSimulator(BaseMetricSimulator):
    """Simulator for Coupling Facility Link Performance metrics"""
    
    def __init__(self, sysplex_name: str):
        super().__init__(sysplex_name)
        self.cf_links = [f"CF{i:02d}" for i in range(1, 5)]
        self.request_types = ["synchronous", "asynchronous"]
    
    def _get_default_baselines(self, lpar_config: LPARConfig) -> Dict[str, float]:
        """CLPR-specific baseline values"""
        base = super()._get_default_baselines(lpar_config)
        base.update({
            'cf_service_time_base': 25.0,  # microseconds
            'sync_request_rate_base': 5000.0,
            'async_request_rate_base': 2000.0
        })
        return base
    
    def simulate(self, lpar_config: LPARConfig) -> List[Dict[str, Any]]:
        """Generate CLPR metrics for an LPAR"""
        self.initialize_baseline(lpar_config)
        
        time_factor = self.get_time_factor(lpar_config)
        base_service_time = self.base_values[lpar_config.name]['cf_service_time_base']
        timestamp = datetime.now()
        metrics = []
        
        for cf_link in self.cf_links:
            # Service time (microseconds)
            service_time = base_service_time * time_factor * (1 + random.uniform(-0.3, 0.5))
            service_time = max(5.0, min(200.0, service_time))  # Clamp between 5-200μs
            
            # Update Prometheus metrics
            CLPR_SERVICE_TIME.labels(
                sysplex=self.sysplex_name,
                lpar=lpar_config.name,
                cf_link=cf_link
            ).observe(service_time)
            
            # Request rates by type
            sync_rate = random.uniform(1000, 10000) * time_factor
            async_rate = random.uniform(500, 3000) * time_factor
            
            CLPR_REQUEST_RATE.labels(
                sysplex=self.sysplex_name,
                lpar=lpar_config.name,
                cf_link=cf_link,
                request_type="synchronous"
            ).set(sync_rate)
            
            CLPR_REQUEST_RATE.labels(
                sysplex=self.sysplex_name,
                lpar=lpar_config.name,
                cf_link=cf_link,
                request_type="asynchronous"
            ).set(async_rate)
            
            # Prepare metrics for storage
            metrics.extend([
                {
                    'timestamp': timestamp.isoformat(),
                    'sysplex': self.sysplex_name,
                    'lpar': lpar_config.name,
                    'cf_link': cf_link,
                    'service_time_microseconds': service_time,
                    'metric_type': 'clpr_service_time'
                },
                {
                    'timestamp': timestamp.isoformat(),
                    'sysplex': self.sysplex_name,
                    'lpar': lpar_config.name,
                    'cf_link': cf_link,
                    'request_type': 'synchronous',
                    'request_rate': sync_rate,
                    'metric_type': 'clpr_request_rate'
                },
                {
                    'timestamp': timestamp.isoformat(),
                    'sysplex': self.sysplex_name,
                    'lpar': lpar_config.name,
                    'cf_link': cf_link,
                    'request_type': 'asynchronous',
                    'request_rate': async_rate,
                    'metric_type': 'clpr_request_rate'
                }
            ])
        
        logger.debug(f"CLPR metrics updated for {lpar_config.name}: {len(metrics)} metrics generated")
        return metrics
    
    def get_metric_type(self) -> str:
        return "clpr_metrics"