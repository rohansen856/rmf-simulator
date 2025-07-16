from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional
import random

from models.lpar import LPARConfig
from utils.logger import logger


class BaseMetricSimulator(ABC):
    """Base class for all metric simulators"""
    
    def __init__(self, sysplex_name: str):
        self.sysplex_name = sysplex_name
        self.base_values = {}
        self.trend_factors = {}
    
    def initialize_baseline(self, lpar_config: LPARConfig) -> Dict[str, float]:
        """Initialize baseline values for an LPAR"""
        if lpar_config.name not in self.base_values:
            self.base_values[lpar_config.name] = self._get_default_baselines(lpar_config)
            self.trend_factors[lpar_config.name] = self._get_default_trend_factors()
        return self.base_values[lpar_config.name]
    
    def _get_default_baselines(self, lpar_config: LPARConfig) -> Dict[str, float]:
        """Override in subclasses to provide specific baseline values"""
        return {
            'cpu_base': 45.0 if lpar_config.workload_type == "online" else 25.0,
            'memory_base': 0.75,
            'io_base': 15.0,
            'cf_base': 25.0,
        }
    
    def _get_default_trend_factors(self) -> Dict[str, float]:
        """Default trend factors for cyclical patterns"""
        return {
            'daily_cycle': random.uniform(0.8, 1.2),
            'weekly_cycle': random.uniform(0.9, 1.1),
            'monthly_cycle': random.uniform(0.95, 1.05),
        }
    
    def get_time_factor(self, lpar_config: LPARConfig) -> float:
        """Calculate time-based performance factor"""
        now = datetime.now()
        current_hour = now.hour
        
        # Peak hours factor
        peak_factor = 1.0
        if current_hour in lpar_config.peak_hours:
            peak_factor = 1.4 if lpar_config.workload_type == "online" else 1.8
        elif lpar_config.workload_type == "batch" and current_hour not in lpar_config.peak_hours:
            peak_factor = 0.3
        
        # Weekly pattern (Monday = higher load)
        weekday_factor = 1.2 if now.weekday() == 0 else 1.0
        
        # Monthly pattern (month-end spike)
        month_end_factor = 1.5 if now.day >= 28 else 1.0
        
        # Seasonal noise
        noise_factor = 1.0 + (random.uniform(-0.1, 0.1))
        
        return peak_factor * weekday_factor * month_end_factor * noise_factor
    
    @abstractmethod
    def simulate(self, lpar_config: LPARConfig) -> List[Dict[str, Any]]:
        """Generate a list of metrics for the given LPAR configuration"""
        pass
    
    @abstractmethod
    def get_metric_type(self) -> str:
        """Return the metric type identifier"""
        pass