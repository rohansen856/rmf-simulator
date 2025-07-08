-- MySQL initialization script for RMF Monitoring Database
-- This file will be executed automatically when the MySQL container starts

-- Set proper character set and collation
ALTER DATABASE rmf_monitoring CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create indexes for better query performance on high-volume tables
-- Note: Tables are created by the Python application, this just adds optimizations

-- Optimize MySQL settings for time-series data
SET GLOBAL innodb_buffer_pool_size = 1073741824; -- 1GB buffer pool
SET GLOBAL innodb_log_file_size = 268435456;     -- 256MB log file
SET GLOBAL innodb_flush_log_at_trx_commit = 2;   -- Better performance for high-volume inserts

-- Create a cleanup event that runs daily to remove old data
-- This is a fallback in case the application cleanup doesn't run
DELIMITER $$

CREATE EVENT IF NOT EXISTS cleanup_old_metrics
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP
DO
BEGIN
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
    
    DELETE FROM cpu_metrics WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
    DELETE FROM memory_metrics WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
    DELETE FROM ldev_utilization_metrics WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
    DELETE FROM ldev_response_time_metrics WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
    DELETE FROM clpr_service_time_metrics WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
    DELETE FROM clpr_request_rate_metrics WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
    DELETE FROM mpb_processing_rate_metrics WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
    DELETE FROM mpb_queue_depth_metrics WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
    DELETE FROM ports_utilization_metrics WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
    DELETE FROM ports_throughput_metrics WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
    DELETE FROM volumes_utilization_metrics WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
    DELETE FROM volumes_iops_metrics WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
END$$

DELIMITER ;

-- Enable the event scheduler
SET GLOBAL event_scheduler = ON;