from prometheus_client import Gauge, Histogram

CPU_UTILIZATION = Gauge('rmf_cpu_utilization_percent', 'CPU utilization', ['sysplex', 'lpar', 'cpu_type'])
MEMORY_USAGE = Gauge('rmf_memory_usage_bytes', 'Memory usage', ['sysplex', 'lpar', 'memory_type'])
LDEV_RESPONSE_TIME = Histogram('rmf_ldev_response_time_seconds', 'LDEV response time', ['sysplex', 'lpar', 'device_type'], buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0])
LDEV_UTILIZATION = Gauge('rmf_ldev_utilization_percent', 'LDEV utilization', ['sysplex', 'lpar', 'device_id'])
CLPR_SERVICE_TIME = Histogram('rmf_clpr_service_time_microseconds', 'CF service time', ['sysplex', 'lpar', 'cf_link'], buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000])
CLPR_REQUEST_RATE = Gauge('rmf_clpr_request_rate', 'CF request rate', ['sysplex', 'lpar', 'cf_link', 'request_type'])
MPB_PROCESSING_RATE = Gauge('rmf_mpb_processing_rate', 'MPB rate', ['sysplex', 'lpar', 'queue_type'])
MPB_QUEUE_DEPTH = Gauge('rmf_mpb_queue_depth', 'MPB queue depth', ['sysplex', 'lpar', 'queue_type'])
PORTS_UTILIZATION = Gauge('rmf_ports_utilization_percent', 'Ports utilization', ['sysplex', 'lpar', 'port_type', 'port_id'])
PORTS_THROUGHPUT = Gauge('rmf_ports_throughput_mbps', 'Ports throughput', ['sysplex', 'lpar', 'port_type', 'port_id'])
VOLUMES_UTILIZATION = Gauge('rmf_volumes_utilization_percent', 'Volume utilization', ['sysplex', 'lpar', 'volume_type', 'volume_id'])
VOLUMES_IOPS = Gauge('rmf_volumes_iops', 'Volume IOPS', ['sysplex', 'lpar', 'volume_type', 'volume_id'])
