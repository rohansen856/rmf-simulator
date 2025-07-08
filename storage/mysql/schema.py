"""Database schema definitions for all tables"""

TABLES = {
    'cpu_metrics': """
        CREATE TABLE IF NOT EXISTS cpu_metrics (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME(3) NOT NULL,
            sysplex VARCHAR(50) NOT NULL,
            lpar VARCHAR(50) NOT NULL,
            cpu_type VARCHAR(50) NOT NULL,
            utilization_percent DECIMAL(5,2) NOT NULL,
            INDEX idx_timestamp (timestamp),
            INDEX idx_lpar_cpu (lpar, cpu_type),
            INDEX idx_sysplex_timestamp (sysplex, timestamp)
        )
    """,
    
    'memory_metrics': """
        CREATE TABLE IF NOT EXISTS memory_metrics (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME(3) NOT NULL,
            sysplex VARCHAR(50) NOT NULL,
            lpar VARCHAR(50) NOT NULL,
            memory_type VARCHAR(50) NOT NULL,
            usage_bytes BIGINT NOT NULL,
            INDEX idx_timestamp (timestamp),
            INDEX idx_lpar_memory (lpar, memory_type),
            INDEX idx_sysplex_timestamp (sysplex, timestamp)
        )
    """,
    
    'ldev_utilization_metrics': """
        CREATE TABLE IF NOT EXISTS ldev_utilization_metrics (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME(3) NOT NULL,
            sysplex VARCHAR(50) NOT NULL,
            lpar VARCHAR(50) NOT NULL,
            device_id VARCHAR(50) NOT NULL,
            utilization_percent DECIMAL(5,2) NOT NULL,
            INDEX idx_timestamp (timestamp),
            INDEX idx_device (device_id),
            INDEX idx_lpar_timestamp (lpar, timestamp)
        )
    """,
    
    'ldev_response_time_metrics': """
        CREATE TABLE IF NOT EXISTS ldev_response_time_metrics (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME(3) NOT NULL,
            sysplex VARCHAR(50) NOT NULL,
            lpar VARCHAR(50) NOT NULL,
            device_type VARCHAR(50) NOT NULL,
            response_time_seconds DECIMAL(10,6) NOT NULL,
            INDEX idx_timestamp (timestamp),
            INDEX idx_device_type (device_type),
            INDEX idx_lpar_timestamp (lpar, timestamp)
        )
    """,
    
    'clpr_service_time_metrics': """
        CREATE TABLE IF NOT EXISTS clpr_service_time_metrics (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME(3) NOT NULL,
            sysplex VARCHAR(50) NOT NULL,
            lpar VARCHAR(50) NOT NULL,
            cf_link VARCHAR(50) NOT NULL,
            service_time_microseconds DECIMAL(10,3) NOT NULL,
            INDEX idx_timestamp (timestamp),
            INDEX idx_cf_link (cf_link),
            INDEX idx_lpar_timestamp (lpar, timestamp)
        )
    """,
    
    'clpr_request_rate_metrics': """
        CREATE TABLE IF NOT EXISTS clpr_request_rate_metrics (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME(3) NOT NULL,
            sysplex VARCHAR(50) NOT NULL,
            lpar VARCHAR(50) NOT NULL,
            cf_link VARCHAR(50) NOT NULL,
            request_type VARCHAR(50) NOT NULL,
            request_rate DECIMAL(10,2) NOT NULL,
            INDEX idx_timestamp (timestamp),
            INDEX idx_cf_link_type (cf_link, request_type),
            INDEX idx_lpar_timestamp (lpar, timestamp)
        )
    """,
    
    'mpb_processing_rate_metrics': """
        CREATE TABLE IF NOT EXISTS mpb_processing_rate_metrics (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME(3) NOT NULL,
            sysplex VARCHAR(50) NOT NULL,
            lpar VARCHAR(50) NOT NULL,
            queue_type VARCHAR(50) NOT NULL,
            processing_rate DECIMAL(10,2) NOT NULL,
            INDEX idx_timestamp (timestamp),
            INDEX idx_queue_type (queue_type),
            INDEX idx_lpar_timestamp (lpar, timestamp)
        )
    """,
    
    'mpb_queue_depth_metrics': """
        CREATE TABLE IF NOT EXISTS mpb_queue_depth_metrics (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME(3) NOT NULL,
            sysplex VARCHAR(50) NOT NULL,
            lpar VARCHAR(50) NOT NULL,
            queue_type VARCHAR(50) NOT NULL,
            queue_depth INT NOT NULL,
            INDEX idx_timestamp (timestamp),
            INDEX idx_queue_type (queue_type),
            INDEX idx_lpar_timestamp (lpar, timestamp)
        )
    """,
    
    'ports_utilization_metrics': """
        CREATE TABLE IF NOT EXISTS ports_utilization_metrics (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME(3) NOT NULL,
            sysplex VARCHAR(50) NOT NULL,
            lpar VARCHAR(50) NOT NULL,
            port_type VARCHAR(50) NOT NULL,
            port_id VARCHAR(50) NOT NULL,
            utilization_percent DECIMAL(5,2) NOT NULL,
            INDEX idx_timestamp (timestamp),
            INDEX idx_port (port_type, port_id),
            INDEX idx_lpar_timestamp (lpar, timestamp)
        )
    """,
    
    'ports_throughput_metrics': """
        CREATE TABLE IF NOT EXISTS ports_throughput_metrics (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME(3) NOT NULL,
            sysplex VARCHAR(50) NOT NULL,
            lpar VARCHAR(50) NOT NULL,
            port_type VARCHAR(50) NOT NULL,
            port_id VARCHAR(50) NOT NULL,
            throughput_mbps DECIMAL(10,2) NOT NULL,
            INDEX idx_timestamp (timestamp),
            INDEX idx_port (port_type, port_id),
            INDEX idx_lpar_timestamp (lpar, timestamp)
        )
    """,
    
    'volumes_utilization_metrics': """
        CREATE TABLE IF NOT EXISTS volumes_utilization_metrics (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME(3) NOT NULL,
            sysplex VARCHAR(50) NOT NULL,
            lpar VARCHAR(50) NOT NULL,
            volume_type VARCHAR(50) NOT NULL,
            volume_id VARCHAR(50) NOT NULL,
            utilization_percent DECIMAL(5,2) NOT NULL,
            INDEX idx_timestamp (timestamp),
            INDEX idx_volume (volume_type, volume_id),
            INDEX idx_lpar_timestamp (lpar, timestamp)
        )
    """,
    
    'volumes_iops_metrics': """
        CREATE TABLE IF NOT EXISTS volumes_iops_metrics (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME(3) NOT NULL,
            sysplex VARCHAR(50) NOT NULL,
            lpar VARCHAR(50) NOT NULL,
            volume_type VARCHAR(50) NOT NULL,
            volume_id VARCHAR(50) NOT NULL,
            iops INT NOT NULL,
            INDEX idx_timestamp (timestamp),
            INDEX idx_volume (volume_type, volume_id),
            INDEX idx_lpar_timestamp (lpar, timestamp)
        )
    """
}

# Table names for easy reference
TABLE_NAMES = list(TABLES.keys())