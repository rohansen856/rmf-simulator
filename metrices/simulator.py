from datetime import datetime
from time import time
import random
from typing import Any, Dict

from metrices.definitions import CLPR_REQUEST_RATE, CLPR_SERVICE_TIME, CPU_UTILIZATION, LDEV_RESPONSE_TIME, LDEV_UTILIZATION, MEMORY_USAGE, MPB_PROCESSING_RATE, MPB_QUEUE_DEPTH, PORTS_THROUGHPUT, PORTS_UTILIZATION, VOLUMES_IOPS, VOLUMES_UTILIZATION
from models.lpar import LPARConfig
from storage.S3.s3 import S3StorageService
from storage.mysql.service import DatabaseService
from storage.mongodb.service import MongoDBService
from utils.logger import logger
from utils.confiig import LPAR_CONFIGS


class MainframeSimulator:
    def __init__(self, enable_mysql: bool = True, enable_mongodb: bool = True, enable_s3: bool = True):
        self.sysplex_name = "SYSPLEX01"
        self.start_time = datetime.now()
        self.base_values = {}
        self.trend_factors = {}

        self.db_service = None
        self.mongo_service = None
        self.s3_service = None

        self.s3_batch_buffer = []
        self.s3_batch_size = 50  # Number of metrics to batch before writing
        self.last_s3_flush = time()
        self.s3_flush_interval = 60  # Flush every 60 seconds even if batch not full

        self.initialize_baselines()
        self._initialize_storage_services(enable_mysql, enable_mongodb, enable_s3)
    
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

    def _initialize_storage_services(self, enable_mysql: bool, enable_mongodb: bool, enable_s3: bool):
        """Initialize storage services based on configuration"""
        try:
            if enable_mysql:
                self.db_service = DatabaseService()
                logger.info("MySQL storage service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MySQL service: {e}")
            self.db_service = None
        
        try:
            if enable_mongodb:
                self.mongo_service = MongoDBService()
                logger.info("MongoDB storage service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB service: {e}")
            self.mongo_service = None
        
        try:
            if enable_s3:
                self.s3_service = S3StorageService()
                logger.info("S3 storage service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize S3 service: {e}")
            self.s3_service = None

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
    
    def _store_metric_to_storages(self, metric_data: Dict[str, Any]):
        """Store metric data to all enabled storage systems"""
        # Add to S3 batch buffer
        if self.s3_service:
            self.s3_batch_buffer.append(metric_data)
            
            # Check if we need to flush the batch
            current_time = time.time()
            if (len(self.s3_batch_buffer) >= self.s3_batch_size or 
                current_time - self.last_s3_flush > self.s3_flush_interval):
                self._flush_s3_batch()
    
    def _flush_s3_batch(self):
        """Flush the S3 batch buffer"""
        if not self.s3_service or not self.s3_batch_buffer:
            return
        
        try:
            self.s3_service.batch_store_metrics(self.s3_batch_buffer)
            logger.debug(f"Flushed {len(self.s3_batch_buffer)} metrics to S3")
            self.s3_batch_buffer.clear()
            self.last_s3_flush = time.time()
        except Exception as e:
            logger.error(f"Error flushing S3 batch: {e}")
    
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

        # database storage
        timestamp = datetime.now()
        if self.db_service:
            try:
                self.db_service.insert_cpu_metric(timestamp, self.sysplex_name, lpar_config.name, "general_purpose", gp_util)
                self.db_service.insert_cpu_metric(timestamp, self.sysplex_name, lpar_config.name, "ziip", ziip_util)
                self.db_service.insert_cpu_metric(timestamp, self.sysplex_name, lpar_config.name, "zaap", zaap_util)
            except Exception as e:
                logger.error(f"Error storing CPU metrics to database: {e}")

        # MongoDB storage
        if self.mongo_service:
            try:
                self.mongo_service.insert_cpu_metric(timestamp, self.sysplex_name, lpar_config.name, "general_purpose", gp_util)
                self.mongo_service.insert_cpu_metric(timestamp, self.sysplex_name, lpar_config.name, "ziip", ziip_util)
                self.mongo_service.insert_cpu_metric(timestamp, self.sysplex_name, lpar_config.name, "zaap", zaap_util)
            except Exception as e:
                logger.error(f"Error storing CPU metrics to MongoDB: {e}")

        # S3 storage (batched)
        cpu_metrics = [
            {
                'timestamp': timestamp.isoformat(),
                'sysplex': self.sysplex_name,
                'lpar': lpar_config.name,
                'cpu_type': 'general_purpose',
                'utilization_percent': gp_util,
                'metric_type': 'cpu_utilization'
            },
            {
                'timestamp': timestamp.isoformat(),
                'sysplex': self.sysplex_name,
                'lpar': lpar_config.name,
                'cpu_type': 'ziip',
                'utilization_percent': ziip_util,
                'metric_type': 'cpu_utilization'
            },
            {
                'timestamp': timestamp.isoformat(),
                'sysplex': self.sysplex_name,
                'lpar': lpar_config.name,
                'cpu_type': 'zaap',
                'utilization_percent': zaap_util,
                'metric_type': 'cpu_utilization'
            }
        ]
        
        for metric in cpu_metrics:
            self._store_metric_to_storages(metric)

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

        # database storage
        timestamp = datetime.now()
        if self.db_service:
            try:
                self.db_service.insert_memory_metric(timestamp, self.sysplex_name, lpar_config.name, "real_storage", used_memory)
                self.db_service.insert_memory_metric(timestamp, self.sysplex_name, lpar_config.name, "virtual_storage", virtual_memory)
                self.db_service.insert_memory_metric(timestamp, self.sysplex_name, lpar_config.name, "csa", csa_memory)
            except Exception as e:
                logger.error(f"Error storing memory metrics to database: {e}")

        # MongoDB storage
        if self.mongo_service:
            try:
                self.mongo_service.insert_memory_metric(timestamp, self.sysplex_name, lpar_config.name, "real_storage", used_memory)
                self.mongo_service.insert_memory_metric(timestamp, self.sysplex_name, lpar_config.name, "virtual_storage", virtual_memory)
                self.mongo_service.insert_memory_metric(timestamp, self.sysplex_name, lpar_config.name, "csa", csa_memory)
            except Exception as e:
                logger.error(f"Error storing memory metrics to MongoDB: {e}")

        # S3 storage (batched)
        memory_metrics = [
            {
                'timestamp': timestamp.isoformat(),
                'sysplex': self.sysplex_name,
                'lpar': lpar_config.name,
                'memory_type': 'real_storage',
                'usage_bytes': used_memory,
                'metric_type': 'memory_usage'
            },
            {
                'timestamp': timestamp.isoformat(),
                'sysplex': self.sysplex_name,
                'lpar': lpar_config.name,
                'memory_type': 'virtual_storage',
                'usage_bytes': virtual_memory,
                'metric_type': 'memory_usage'
            },
            {
                'timestamp': timestamp.isoformat(),
                'sysplex': self.sysplex_name,
                'lpar': lpar_config.name,
                'memory_type': 'csa',
                'usage_bytes': csa_memory,
                'metric_type': 'memory_usage'
            }
        ]
        
        for metric in memory_metrics:
            self._store_metric_to_storages(metric)
    
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
        
        timestamp = datetime.now()
        ldev_metrics = []
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

                # database storage
                if self.db_service:
                    try:
                        self.db_service.insert_ldev_response_time_metric(
                        timestamp, self.sysplex_name, lpar_config.name, device_type, response_time / 1000.0
                        )
                        self.db_service.insert_ldev_utilization_metric(
                            timestamp, self.sysplex_name, lpar_config.name, device_id, utilization
                        )
                    except Exception as e:
                        logger.error(f"Error storing LDEV metrics to database: {e}")

                # MongoDB storage
                if self.mongo_service:
                    try:
                        self.mongo_service.insert_ldev_response_time_metric(
                            timestamp, self.sysplex_name, lpar_config.name, device_type, response_time / 1000.0
                        )
                        self.mongo_service.insert_ldev_utilization_metric(
                            timestamp, self.sysplex_name, lpar_config.name, device_id, utilization
                        )
                    except Exception as e:
                        logger.error(f"Error storing LDEV metrics to MongoDB: {e}")

                # Prepare metrics for batch storage
                ldev_metrics.extend([
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
        # S3 storage (batched)
        for metric in ldev_metrics:
            self._store_metric_to_storages(metric)
    
    def simulate_clpr_metrics(self, lpar_config: LPARConfig):
        """Generate realistic Coupling Facility Link Performance metrics"""
        time_factor = self.get_time_factor(lpar_config)
        base_service_time = self.base_values[lpar_config.name]['cf_base']
        
        # Multiple CF links per LPAR
        cf_links = [f"CF{i:02d}" for i in range(1, 5)]
        
        timestamp = datetime.now()
        clpr_metrics = []
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

            # database storage
            if self.db_service:
                try:
                    self.db_service.insert_clpr_service_time_metric(
                        timestamp, self.sysplex_name, lpar_config.name, cf_link, service_time
                    )
                    self.db_service.insert_clpr_request_rate_metric(
                        timestamp, self.sysplex_name, lpar_config.name, cf_link, "synchronous", sync_rate
                    )
                    self.db_service.insert_clpr_request_rate_metric(
                        timestamp, self.sysplex_name, lpar_config.name, cf_link, "asynchronous", async_rate
                    )
                except Exception as e:
                    logger.error(f"Error storing CLPR metrics to database: {e}")

            # MongoDB storage
            if self.mongo_service:
                try:
                    self.mongo_service.insert_clpr_service_time_metric(
                        timestamp, self.sysplex_name, lpar_config.name, cf_link, service_time
                    )
                    self.mongo_service.insert_clpr_request_rate_metric(
                        timestamp, self.sysplex_name, lpar_config.name, cf_link, "synchronous", sync_rate
                    )
                    self.mongo_service.insert_clpr_request_rate_metric(
                        timestamp, self.sysplex_name, lpar_config.name, cf_link, "asynchronous", async_rate
                    )
                except Exception as e:
                    logger.error(f"Error storing CLPR metrics to MongoDB: {e}")

            # Prepare metrics for batch storage
            clpr_metrics.extend([
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
        # S3 storage (batched)
        for metric in clpr_metrics:
            self._store_metric_to_storages(metric)
    
    def simulate_mpb_metrics(self, lpar_config: LPARConfig):
        """Generate realistic Message Processing Block metrics"""
        time_factor = self.get_time_factor(lpar_config)
        
        queue_types = ["CICS", "IMS", "MQ", "BATCH"]
        
        timestamp = datetime.now()
        mpb_metrics = []
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

            # database storage
            if self.db_service:
                try:
                    self.db_service.insert_mpb_processing_rate_metric(
                        timestamp, self.sysplex_name, lpar_config.name, queue_type, processing_rate
                    )
                    self.db_service.insert_mpb_queue_depth_metric(
                        timestamp, self.sysplex_name, lpar_config.name, queue_type, queue_depth
                    )
                except Exception as e:
                    logger.error(f"Error storing MPB metrics to database: {e}")

            # MongoDB storage
            if self.mongo_service:
                try:
                    self.mongo_service.insert_mpb_processing_rate_metric(
                        timestamp, self.sysplex_name, lpar_config.name, queue_type, processing_rate
                    )
                    self.mongo_service.insert_mpb_queue_depth_metric(
                        timestamp, self.sysplex_name, lpar_config.name, queue_type, queue_depth
                    )
                except Exception as e:
                    logger.error(f"Error storing MPB metrics to MongoDB: {e}")

            # Prepare metrics for batch storage
            mpb_metrics.extend([
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
        # S3 storage (batched)
        for metric in mpb_metrics:
            self._store_metric_to_storages(metric)
    
    def simulate_ports_metrics(self, lpar_config: LPARConfig):
        """Generate realistic port utilization and throughput metrics"""
        time_factor = self.get_time_factor(lpar_config)
        
        port_types = {
            "OSA": {"count": 4, "max_throughput": 1000, "base_util": 35.0},
            "Hipersocket": {"count": 2, "max_throughput": 10000, "base_util": 15.0},
            "FICON": {"count": 8, "max_throughput": 400, "base_util": 45.0},
        }
        
        timestamp = datetime.now()
        ports_metrics = []
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

                # database storage
                if self.db_service:
                    try:
                        self.db_service.insert_ports_utilization_metric(
                            timestamp, self.sysplex_name, lpar_config.name, port_type, port_id, utilization
                        )
                        self.db_service.insert_ports_throughput_metric(
                            timestamp, self.sysplex_name, lpar_config.name, port_type, port_id, throughput
                        )
                    except Exception as e:
                        logger.error(f"Error storing ports metrics to database: {e}")

                # MongoDB storage
                if self.mongo_service:
                    try:
                        self.mongo_service.insert_ports_utilization_metric(
                            timestamp, self.sysplex_name, lpar_config.name, port_type, port_id, utilization
                        )
                        self.mongo_service.insert_ports_throughput_metric(
                            timestamp, self.sysplex_name, lpar_config.name, port_type, port_id, throughput
                        )
                    except Exception as e:
                        logger.error(f"Error storing ports metrics to MongoDB: {e}")

                # Prepare metrics for batch storage
                ports_metrics.extend([
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
        # S3 storage (batched)
        for metric in ports_metrics:
            self._store_metric_to_storages(metric)

    
    def simulate_volumes_metrics(self, lpar_config: LPARConfig):
        """Generate realistic volume metrics"""
        time_factor = self.get_time_factor(lpar_config)
        
        volume_types = {
            "SYSRES": {"count": 2, "base_util": 60.0, "base_iops": 1500},
            "WORK": {"count": 15, "base_util": 45.0, "base_iops": 800},
            "USER": {"count": 25, "base_util": 35.0, "base_iops": 600},
            "TEMP": {"count": 8, "base_util": 25.0, "base_iops": 400},
        }
        
        timestamp = datetime.now()
        volumes_metrics = []
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

                # database storage
                if self.db_service:
                    try:
                        self.db_service.insert_volumes_utilization_metric(
                            timestamp, self.sysplex_name, lpar_config.name, volume_type, volume_id, utilization
                        )
                        self.db_service.insert_volumes_iops_metric(
                            timestamp, self.sysplex_name, lpar_config.name, volume_type, volume_id, iops
                        )
                    except Exception as e:
                        logger.error(f"Error storing volumes metrics to database: {e}")

                # MongoDB storage
                if self.mongo_service:
                    try:
                        self.mongo_service.insert_volumes_utilization_metric(
                            timestamp, self.sysplex_name, lpar_config.name, volume_type, volume_id, utilization
                        )
                        self.mongo_service.insert_volumes_iops_metric(
                            timestamp, self.sysplex_name, lpar_config.name, volume_type, volume_id, iops
                        )
                    except Exception as e:
                        logger.error(f"Error storing volumes metrics to MongoDB: {e}")

                # Prepare metrics for batch storage
                volumes_metrics.extend([
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
        # S3 storage (batched)
        for metric in volumes_metrics:
            self._store_metric_to_storages(metric)
    
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
        
        # Force flush S3 batch after each complete update cycle
        self._flush_s3_batch()

# Initialize simulator
simulator = MainframeSimulator(
    enable_mysql=False,
    enable_mongodb=False,
    enable_s3=False
)