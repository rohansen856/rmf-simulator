from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
import asyncio
import logging
from datetime import datetime, time
import random
import math
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

app = FastAPI(
    title="RMF Monitor III Data Simulator",
    description="Production-ready z/OS metrics simulator with realistic workload patterns",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus Metrics Definitions
class MetricType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    LDEV = "ldev"
    CLPR = "clpr"
    MPB = "mpb"
    PORTS = "ports"
    VOLUMES = "volumes"

@dataclass
class LPARConfig:
    name: str
    cpu_capacity: int
    memory_gb: int
    workload_type: str
    peak_hours: List[int]

# LPAR Configurations
LPAR_CONFIGS = [
    LPARConfig("PROD01", 16, 64, "online", [8, 9, 10, 14, 15, 16]),
    LPARConfig("PROD02", 12, 48, "online", [8, 9, 10, 14, 15, 16]),
    LPARConfig("BATCH01", 8, 32, "batch", [22, 23, 0, 1, 2, 3, 4, 5]),
    LPARConfig("TEST01", 4, 16, "mixed", [9, 10, 11, 15, 16, 17]),
]

# Prometheus metrics
CPU_UTILIZATION = Gauge('rmf_cpu_utilization_percent', 'CPU utilization percentage', ['sysplex', 'lpar', 'cpu_type'])
MEMORY_USAGE = Gauge('rmf_memory_usage_bytes', 'Memory usage in bytes', ['sysplex', 'lpar', 'memory_type'])
LDEV_RESPONSE_TIME = Histogram('rmf_ldev_response_time_seconds', 'LDEV response time in seconds', ['sysplex', 'lpar', 'device_type'], buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0])
LDEV_UTILIZATION = Gauge('rmf_ldev_utilization_percent', 'LDEV utilization percentage', ['sysplex', 'lpar', 'device_id'])
CLPR_SERVICE_TIME = Histogram('rmf_clpr_service_time_microseconds', 'Coupling facility service time', ['sysplex', 'lpar', 'cf_link'], buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000])
CLPR_REQUEST_RATE = Gauge('rmf_clpr_request_rate', 'Coupling facility request rate', ['sysplex', 'lpar', 'cf_link', 'request_type'])
MPB_PROCESSING_RATE = Gauge('rmf_mpb_processing_rate', 'Message processing rate', ['sysplex', 'lpar', 'queue_type'])
MPB_QUEUE_DEPTH = Gauge('rmf_mpb_queue_depth', 'Message queue depth', ['sysplex', 'lpar', 'queue_type'])
PORTS_UTILIZATION = Gauge('rmf_ports_utilization_percent', 'Port utilization percentage', ['sysplex', 'lpar', 'port_type', 'port_id'])
PORTS_THROUGHPUT = Gauge('rmf_ports_throughput_mbps', 'Port throughput in MB/s', ['sysplex', 'lpar', 'port_type', 'port_id'])
VOLUMES_UTILIZATION = Gauge('rmf_volumes_utilization_percent', 'Volume utilization percentage', ['sysplex', 'lpar', 'volume_type', 'volume_id'])
VOLUMES_IOPS = Gauge('rmf_volumes_iops', 'Volume IOPS', ['sysplex', 'lpar', 'volume_type', 'volume_id'])

class MainframeSimulator:
    def __init__(self):
        self.sysplex_name = "SYSPLEX01"
        self.start_time = datetime.now()
        self.base_values = {}
        self.trend_factors = {}
        self.initialize_baselines()
    
    def initialize_baselines(self):
        """Initialize baseline values for realistic simulation"""
        for lpar in LPAR_CONFIGS:
            self.base_values[lpar.name] = {
                'cpu_base': 45.0 if lpar.workload_type == "online" else 25.0,
                'memory_base': 0.75,  # 75% base utilization
                'io_base': 15.0,  # 15ms base response time
                'cf_base': 25.0,  # 25 microseconds base service time
            }
            
            # Initialize trend factors for cyclical patterns
            self.trend_factors[lpar.name] = {
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
            peak_factor = 0.3  # Low activity during non-batch hours
        
        # Weekly pattern (Monday = higher load)
        weekday_factor = 1.2 if now.weekday() == 0 else 1.0
        
        # Monthly pattern (month-end spike)
        month_end_factor = 1.5 if now.day >= 28 else 1.0
        
        # Seasonal noise
        noise_factor = 1.0 + (random.uniform(-0.1, 0.1))
        
        return peak_factor * weekday_factor * month_end_factor * noise_factor
    
    def simulate_cpu_metrics(self, lpar_config: LPARConfig):
        """Generate realistic CPU metrics"""
        time_factor = self.get_time_factor(lpar_config)
        base_util = self.base_values[lpar_config.name]['cpu_base']
        
        # General purpose CPU utilization
        gp_util = min(95.0, base_util * time_factor)
        
        # Specialty engine utilization (zIIP/zAAP)
        ziip_util = min(75.0, gp_util * 0.6)
        zaap_util = min(70.0, gp_util * 0.4)
        
        # Update metrics
        CPU_UTILIZATION.labels(
            sysplex=self.sysplex_name,
            lpar=lpar_config.name,
            cpu_type="general_purpose"
        ).set(gp_util)
        
        CPU_UTILIZATION.labels(
            sysplex=self.sysplex_name,
            lpar=lpar_config.name,
            cpu_type="ziip"
        ).set(ziip_util)
        
        CPU_UTILIZATION.labels(
            sysplex=self.sysplex_name,
            lpar=lpar_config.name,
            cpu_type="zaap"
        ).set(zaap_util)
        
        logger.debug(f"CPU metrics updated for {lpar_config.name}: GP={gp_util:.1f}%, zIIP={ziip_util:.1f}%")
    
    def simulate_memory_metrics(self, lpar_config: LPARConfig):
        """Generate realistic memory metrics"""
        time_factor = self.get_time_factor(lpar_config)
        base_util = self.base_values[lpar_config.name]['memory_base']
        
        # Calculate memory usage
        memory_util = min(0.90, base_util * time_factor)
        total_memory = lpar_config.memory_gb * 1024 * 1024 * 1024  # Convert to bytes
        used_memory = int(total_memory * memory_util)
        
        # Real storage
        MEMORY_USAGE.labels(
            sysplex=self.sysplex_name,
            lpar=lpar_config.name,
            memory_type="real_storage"
        ).set(used_memory)
        
        # Virtual storage (typically 3-10x real storage)
        virtual_multiplier = 4.0 if lpar_config.workload_type == "online" else 6.0
        virtual_memory = int(total_memory * virtual_multiplier)
        
        MEMORY_USAGE.labels(
            sysplex=self.sysplex_name,
            lpar=lpar_config.name,
            memory_type="virtual_storage"
        ).set(virtual_memory)
        
        # Common Service Area (CSA)
        csa_memory = random.randint(200_000_000, 800_000_000)  # 200-800MB
        MEMORY_USAGE.labels(
            sysplex=self.sysplex_name,
            lpar=lpar_config.name,
            memory_type="csa"
        ).set(csa_memory)
    
    def simulate_ldev_metrics(self, lpar_config: LPARConfig):
        """Generate realistic LDEV (storage device) metrics"""
        time_factor = self.get_time_factor(lpar_config)
        base_response = self.base_values[lpar_config.name]['io_base']
        
        # Different device types with different characteristics
        device_types = {
            "3390": {"count": 20, "response_base": 8.0, "util_base": 40.0},
            "flashcopy": {"count": 8, "response_base": 2.0, "util_base": 55.0},
            "tape": {"count": 12, "response_base": 45.0, "util_base": 25.0},
        }
        
        for device_type, config in device_types.items():
            for i in range(config["count"]):
                device_id = f"{device_type}_{i:02d}"
                
                # Response time calculation
                response_time = config["response_base"] * time_factor * (1 + random.uniform(-0.2, 0.3))
                response_time = max(1.0, min(100.0, response_time))  # Clamp between 1-100ms
                
                # Utilization calculation
                utilization = config["util_base"] * time_factor * (1 + random.uniform(-0.3, 0.4))
                utilization = max(5.0, min(95.0, utilization))  # Clamp between 5-95%
                
                # Update metrics
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
    
    def simulate_clpr_metrics(self, lpar_config: LPARConfig):
        """Generate realistic Coupling Facility Link Performance metrics"""
        time_factor = self.get_time_factor(lpar_config)
        base_service_time = self.base_values[lpar_config.name]['cf_base']
        
        # Multiple CF links per LPAR
        cf_links = [f"CF{i:02d}" for i in range(1, 5)]
        
        for cf_link in cf_links:
            # Service time (microseconds)
            service_time = base_service_time * time_factor * (1 + random.uniform(-0.3, 0.5))
            service_time = max(5.0, min(200.0, service_time))  # Clamp between 5-200μs
            
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
    
    def simulate_mpb_metrics(self, lpar_config: LPARConfig):
        """Generate realistic Message Processing Block metrics"""
        time_factor = self.get_time_factor(lpar_config)
        
        queue_types = ["CICS", "IMS", "MQ", "BATCH"]
        
        for queue_type in queue_types:
            # Processing rate varies by queue type and workload
            base_rate = {
                "CICS": 5000,
                "IMS": 3000,
                "MQ": 2000,
                "BATCH": 500
            }.get(queue_type, 1000)
            
            processing_rate = base_rate * time_factor * (1 + random.uniform(-0.2, 0.3))
            processing_rate = max(100, processing_rate)
            
            # Queue depth increases with load
            queue_depth = max(1, int(processing_rate / 1000 * random.uniform(0.1, 0.5)))
            
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
    
    def simulate_ports_metrics(self, lpar_config: LPARConfig):
        """Generate realistic port utilization and throughput metrics"""
        time_factor = self.get_time_factor(lpar_config)
        
        port_types = {
            "OSA": {"count": 4, "max_throughput": 1000, "base_util": 35.0},
            "Hipersocket": {"count": 2, "max_throughput": 10000, "base_util": 15.0},
            "FICON": {"count": 8, "max_throughput": 400, "base_util": 45.0},
        }
        
        for port_type, config in port_types.items():
            for i in range(config["count"]):
                port_id = f"{port_type}_{i:02d}"
                
                # Utilization
                utilization = config["base_util"] * time_factor * (1 + random.uniform(-0.4, 0.6))
                utilization = max(5.0, min(85.0, utilization))
                
                # Throughput
                throughput = config["max_throughput"] * (utilization / 100.0)
                throughput = max(1.0, throughput)
                
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
    
    def simulate_volumes_metrics(self, lpar_config: LPARConfig):
        """Generate realistic volume metrics"""
        time_factor = self.get_time_factor(lpar_config)
        
        volume_types = {
            "SYSRES": {"count": 2, "base_util": 60.0, "base_iops": 1500},
            "WORK": {"count": 15, "base_util": 45.0, "base_iops": 800},
            "USER": {"count": 25, "base_util": 35.0, "base_iops": 600},
            "TEMP": {"count": 8, "base_util": 25.0, "base_iops": 400},
        }
        
        for volume_type, config in volume_types.items():
            for i in range(config["count"]):
                volume_id = f"{volume_type}{i:03d}"
                
                # Utilization
                utilization = config["base_util"] * time_factor * (1 + random.uniform(-0.3, 0.4))
                utilization = max(10.0, min(90.0, utilization))
                
                # IOPS
                iops = config["base_iops"] * time_factor * (1 + random.uniform(-0.4, 0.6))
                iops = max(50, int(iops))
                
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
    
    async def update_all_metrics(self):
        """Update all metrics for all LPARs"""
        for lpar_config in LPAR_CONFIGS:
            try:
                self.simulate_cpu_metrics(lpar_config)
                self.simulate_memory_metrics(lpar_config)
                self.simulate_ldev_metrics(lpar_config)
                self.simulate_clpr_metrics(lpar_config)
                self.simulate_mpb_metrics(lpar_config)
                self.simulate_ports_metrics(lpar_config)
                self.simulate_volumes_metrics(lpar_config)
                
                logger.debug(f"Updated metrics for {lpar_config.name}")
            except Exception as e:
                logger.error(f"Error updating metrics for {lpar_config.name}: {e}")

# Initialize simulator
simulator = MainframeSimulator()

# Background task to update metrics
async def metrics_updater():
    """Background task that updates metrics every 15 seconds"""
    while True:
        try:
            await simulator.update_all_metrics()
            logger.info("Metrics updated successfully")
        except Exception as e:
            logger.error(f"Error in metrics updater: {e}")
        await asyncio.sleep(15)

@app.on_event("startup")
async def startup_event():
    """Start the metrics updater on application startup"""
    asyncio.create_task(metrics_updater())
    logger.info("RMF Monitor III Data Simulator started")

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "name": "RMF Monitor III Data Simulator",
        "version": "1.0.0",
        "sysplex": simulator.sysplex_name,
        "lpars": [lpar.name for lpar in LPAR_CONFIGS],
        "metrics_endpoint": "/metrics",
        "health_endpoint": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return {"status": "ready", "timestamp": datetime.now().isoformat()}

@app.get("/startup")
async def startup_check():
    """Startup check endpoint"""
    return {"status": "started", "timestamp": datetime.now().isoformat()}

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.get("/system-info")
async def get_system_info():
    """Get current system information and metrics summary"""
    current_time = datetime.now()
    
    system_info = {
        "sysplex": simulator.sysplex_name,
        "timestamp": current_time.isoformat(),
        "uptime_seconds": int((current_time - simulator.start_time).total_seconds()),
        "lpars": []
    }
    
    for lpar in LPAR_CONFIGS:
        time_factor = simulator.get_time_factor(lpar)
        lpar_info = {
            "name": lpar.name,
            "workload_type": lpar.workload_type,
            "cpu_capacity": lpar.cpu_capacity,
            "memory_gb": lpar.memory_gb,
            "peak_hours": lpar.peak_hours,
            "current_load_factor": round(time_factor, 2),
            "is_peak_hour": current_time.hour in lpar.peak_hours
        }
        system_info["lpars"].append(lpar_info)
    
    return system_info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)