MONGO_HOST=localhost                 # MongoDB server host
MONGO_PORT=27017                    # MongoDB server port
MONGO_DATABASE=rmf_monitoring       # Database name
MONGO_USERNAME=rmf_user             # Database username
MONGO_PASSWORD=secure_password      # Database password
MONGO_AUTH_SOURCE=admin             # Authentication database
MONGO_REPLICA_SET=                  # Replica set name (optional)
MONGO_CONNECTION_TIMEOUT=5000       # Connection timeout in milliseconds
MONGO_SERVER_SELECTION_TIMEOUT=5000 # Server selection timeout
MONGO_MAX_POOL_SIZE=50              # Maximum connection pool size
MONGO_MIN_POOL_SIZE=5               # Minimum connection pool size
```

#### S3/MinIO Configuration

```bash
# S3-Compatible Storage Settings
S3_ENDPOINT_URL=http://localhost:9000  # S3 endpoint URL
S3_ACCESS_KEY=minioadmin              # Access key
S3_SECRET_KEY=minioadmin123           # Secret key
S3_BUCKET_NAME=rmf-metrics            # Bucket name
S3_REGION=us-east-1                   # AWS region
S3_USE_SSL=false                      # Use SSL/TLS
S3_SIGNATURE_VERSION=s3v4             # Signature version
S3_ADDRESSING_STYLE=virtual           # Addressing style: virtual, path
S3_MAX_POOL_CONNECTIONS=50            # Maximum pool connections
```

### Monitoring Configuration

```bash
# Prometheus Configuration
PROMETHEUS_METRICS_PATH=/metrics      # Metrics endpoint path
PROMETHEUS_PUSH_GATEWAY_URL=          # Push gateway URL (optional)
PROMETHEUS_JOB_NAME=rmf-simulator     # Job name for metrics
PROMETHEUS_INSTANCE_ID=               # Instance ID (auto-generated if empty)

# Grafana Configuration
GRAFANA_URL=http://localhost:3000     # Grafana URL
GRAFANA_API_KEY=                      # Grafana API key
GRAFANA_ADMIN_PASSWORD=admin          # Admin password

# Alertmanager Configuration
ALERTMANAGER_URL=http://localhost:9093 # Alertmanager URL
ALERTMANAGER_API_PATH=/api/v1         # API path
```

### Security Configuration

```bash
# Authentication Settings
JWT_SECRET_KEY=super-secret-key  # JWT signing key
JWT_ALGORITHM=HS256                   # JWT algorithm
JWT_EXPIRATION_HOURS=24              # Token expiration time
API_KEY_HEADER=X-API-Key             # API key header name
CORS_ORIGINS=*                       # CORS allowed origins
CORS_METHODS=GET,POST,PUT,DELETE     # CORS allowed methods
CORS_HEADERS=*                       # CORS allowed headers

# TLS Configuration
TLS_CERT_FILE=/certs/server.crt      # TLS certificate file
TLS_KEY_FILE=/certs/server.key       # TLS private key file
TLS_CA_FILE=/certs/ca.crt            # TLS CA certificate file
```

### Performance Configuration

```bash
# Performance Tuning
MAX_CONCURRENT_REQUESTS=1000         # Maximum concurrent requests
REQUEST_TIMEOUT=30                   # Request timeout in seconds
KEEP_ALIVE_TIMEOUT=65               # Keep-alive timeout
MAX_REQUEST_SIZE=16777216           # Maximum request size in bytes
WORKER_CONNECTIONS=1000             # Worker connections per process
BACKLOG=2048                        # Listen backlog size

# Memory Configuration
MEMORY_LIMIT=2Gi                    # Memory limit
HEAP_SIZE=1Gi                       # Heap size for JVM components
GC_THRESHOLD=0.7                    # Garbage collection threshold
```

---

## 📄 Configuration Files

### Application Configuration

Create `config/app.yaml`:

```yaml
# Application configuration
application:
  name: "RMF Monitor III Data Simulator"
  version: "1.0.0"
  environment: "${ENVIRONMENT:-production}"
  debug: false
  
  # Server settings
  server:
    host: "${HOST:-0.0.0.0}"
    port: ${PORT:-8000}
    workers: ${WORKERS:-4}
    reload: ${RELOAD:-false}
    
  # Logging configuration
  logging:
    level: "${LOG_LEVEL:-INFO}"
    format: "json"
    output: "stdout"
    
    # Log rotation
    rotation:
      max_size: "100MB"
      max_files: 10
      max_age: "30d"

# Simulation settings
simulation:
  interval: ${SIMULATION_INTERVAL:-15}
  sysplex_name: "${SYSPLEX_NAME:-SYSPLEX01}"
  batch_size: ${BATCH_SIZE:-50}
  flush_interval: ${FLUSH_INTERVAL:-60}
  
  # Workload patterns
  patterns:
    enable_peak_hours: true
    enable_seasonal_variation: true
    enable_workload_correlation: true
    noise_factor: 0.1

# Feature flags
features:
  mysql_storage: ${MYSQL_ENABLED:-true}
  mongodb_storage: ${MONGODB_ENABLED:-true}
  s3_storage: ${S3_ENABLED:-true}
  prometheus_metrics: ${PROMETHEUS_ENABLED:-true}
  health_checks: ${HEALTH_CHECKS_ENABLED:-true}
  authentication: ${AUTH_ENABLED:-false}
  rate_limiting: ${RATE_LIMITING_ENABLED:-true}
```

### Database Configuration

Create `config/database.yaml`:

```yaml
# Database configuration
databases:
  mysql:
    enabled: ${MYSQL_ENABLED:-true}
    host: "${MYSQL_HOST:-localhost}"
    port: ${MYSQL_PORT:-3306}
    database: "${MYSQL_DATABASE:-rmf_monitoring}"
    user: "${MYSQL_USER:-rmf_user}"
    password: "${MYSQL_PASSWORD}"
    
    # Connection pool settings
    pool:
      max_connections: ${MYSQL_MAX_CONNECTIONS:-100}
      min_connections: ${MYSQL_MIN_CONNECTIONS:-10}
      connection_timeout: ${MYSQL_CONNECTION_TIMEOUT:-5000}
      idle_timeout: 300000
      max_lifetime: 3600000
      
    # Performance settings
    charset: "${MYSQL_CHARSET:-utf8mb4}"
    collation: "${MYSQL_COLLATION:-utf8mb4_unicode_ci}"
    autocommit: true
    isolation_level: "READ_COMMITTED"
    
  mongodb:
    enabled: ${MONGODB_ENABLED:-true}
    host: "${MONGO_HOST:-localhost}"
    port: ${MONGO_PORT:-27017}
    database: "${MONGO_DATABASE:-rmf_monitoring}"
    username: "${MONGO_USERNAME:-rmf_user}"
    password: "${MONGO_PASSWORD}"
    auth_source: "${MONGO_AUTH_SOURCE:-admin}"
    replica_set: "${MONGO_REPLICA_SET:-}"
    
    # Connection settings
    connection_timeout: ${MONGO_CONNECTION_TIMEOUT:-5000}
    server_selection_timeout: ${MONGO_SERVER_SELECTION_TIMEOUT:-5000}
    max_pool_size: ${MONGO_MAX_POOL_SIZE:-50}
    min_pool_size: ${MONGO_MIN_POOL_SIZE:-5}
    
    # Performance settings
    retry_writes: true
    retry_reads: true
    read_preference: "secondaryPreferred"
    write_concern:
      w: "majority"
      j: true
      wtimeout: 5000
      
  s3:
    enabled: ${S3_ENABLED:-true}
    endpoint_url: "${S3_ENDPOINT_URL:-http://localhost:9000}"
    access_key: "${S3_ACCESS_KEY:-minioadmin}"
    secret_key: "${S3_SECRET_KEY}"
    bucket_name: "${S3_BUCKET_NAME:-rmf-metrics}"
    region: "${S3_REGION:-us-east-1}"
    use_ssl: ${S3_USE_SSL:-false}
    signature_version: "${S3_SIGNATURE_VERSION:-s3v4}"
    addressing_style: "${S3_ADDRESSING_STYLE:-virtual}"
    max_pool_connections: ${S3_MAX_POOL_CONNECTIONS:-50}
    
    # Lifecycle policies
    lifecycle:
      metrics_retention_days: 90
      archive_retention_days: 2555  # 7 years
      transition_to_ia_days: 30
      transition_to_glacier_days: 90
```

### Monitoring Configuration

Create `config/monitoring.yaml`:

```yaml
# Monitoring configuration
monitoring:
  prometheus:
    enabled: ${PROMETHEUS_ENABLED:-true}
    metrics_path: "${PROMETHEUS_METRICS_PATH:-/metrics}"
    push_gateway_url: "${PROMETHEUS_PUSH_GATEWAY_URL:-}"
    job_name: "${PROMETHEUS_JOB_NAME:-rmf-simulator}"
    instance_id: "${PROMETHEUS_INSTANCE_ID:-}"
    
    # Metric collection settings
    collection:
      interval: 15
      timeout: 10
      honor_labels: true
      
    # Custom metrics
    custom_metrics:
      - name: "rmf_business_metrics"
        type: "counter"
        help: "Business-specific metrics"
        labels: ["metric_type", "business_unit"]
        
  grafana:
    enabled: ${GRAFANA_ENABLED:-true}
    url: "${GRAFANA_URL:-http://localhost:3000}"
    api_key: "${GRAFANA_API_KEY:-}"
    admin_password: "${GRAFANA_ADMIN_PASSWORD:-admin}"
    
    # Dashboard settings
    dashboards:
      auto_import: true
      update_interval: 300
      default_refresh: "30s"
      
  alertmanager:
    enabled: ${ALERTMANAGER_ENABLED:-true}
    url: "${ALERTMANAGER_URL:-http://localhost:9093}"
    api_path: "${ALERTMANAGER_API_PATH:-/api/v1}"
    
    # Alert routing
    routing:
      group_by: ["alertname", "sysplex"]
      group_wait: "10s"
      group_interval: "30s"
      repeat_interval: "12h"
      
  logging:
    enabled: true
    level: "${LOG_LEVEL:-INFO}"
    format: "json"
    
    # Log aggregation
    aggregation:
      enabled: ${LOG_AGGREGATION_ENABLED:-false}
      elasticsearch_url: "${ELASTICSEARCH_URL:-}"
      index_pattern: "rmf-simulator-logs-*"
      
  tracing:
    enabled: ${TRACING_ENABLED:-false}
    jaeger_url: "${JAEGER_URL:-http://localhost:14268}"
    service_name: "rmf-simulator"
    sampling_rate: 0.1
```

---

## 🖥️ LPAR Configuration

### Default LPAR Configuration

Create `config/lpars.yaml`:

```yaml
# LPAR configuration
lpars:
  - name: "PROD01"
    description: "Production LPAR 1"
    cpu_capacity: 16
    memory_gb: 64
    workload_type: "online"
    peak_hours: [8, 9, 10, 14, 15, 16]
    
    # Workload characteristics
    workload:
      base_cpu_utilization: 45.0
      base_memory_utilization: 0.75
      base_io_response_time: 15.0
      base_cf_service_time: 25.0
      
    # Specialty processors
    specialty_processors:
      ziip:
        count: 4
        utilization_factor: 0.6
      zaap:
        count: 2
        utilization_factor: 0.4
        
    # Storage configuration
    storage:
      devices:
        - type: "3390"
          count: 20
          base_utilization: 40.0
          base_response_time: 8.0
        - type: "flashcopy"
          count: 8
          base_utilization: 55.0
          base_response_time: 2.0
        - type: "tape"
          count: 12
          base_utilization: 25.0
          base_response_time: 45.0
          
    # Network configuration
    network:
      ports:
        - type: "OSA"
          count: 4
          max_throughput: 1000
          base_utilization: 35.0
        - type: "Hipersocket"
          count: 2
          max_throughput: 10000
          base_utilization: 15.0
        - type: "FICON"
          count: 8
          max_throughput: 400
          base_utilization: 45.0
          
    # Volume configuration
    volumes:
      - type: "SYSRES"
        count: 2
        base_utilization: 60.0
        base_iops: 1500
      - type: "WORK"
        count: 15
        base_utilization: 45.0
        base_iops: 800
      - type: "USER"
        count: 25
        base_utilization: 35.0
        base_iops: 600
      - type: "TEMP"
        count: 8
        base_utilization: 25.0
        base_iops: 400
        
  - name: "PROD02"
    description: "Production LPAR 2"
    cpu_capacity: 12
    memory_gb: 48
    workload_type: "online"
    peak_hours: [8, 9, 10, 14, 15, 16]
    
    # Inherit base configuration with overrides
    inherits: "PROD01"
    overrides:
      workload:
        base_cpu_utilization: 50.0
        base_memory_utilization: 0.8
        
  - name: "BATCH01"
    description: "Batch Processing LPAR"
    cpu_capacity: 8
    memory_gb: 32
    workload_type: "batch"
    peak_hours: [22, 23, 0, 1, 2, 3, 4, 5]
    
    # Batch-specific configuration
    workload:
      base_cpu_utilization: 25.0
      base_memory_utilization: 0.6
      base_io_response_time: 20.0
      base_cf_service_time: 30.0
      
    # Batch processing patterns
    batch_patterns:
      daily_jobs:
        start_time: "22:00"
        duration: 360  # 6 hours
        cpu_spike_factor: 2.0
        memory_spike_factor: 1.5
      weekly_jobs:
        day_of_week: "sunday"
        start_time: "01:00"
        duration: 180  # 3 hours
        cpu_spike_factor: 3.0
      monthly_jobs:
        day_of_month: [1, 15]
        start_time: "23:00"
        duration: 480  # 8 hours
        cpu_spike_factor: 2.5
        
  - name: "TEST01"
    description: "Test Environment LPAR"
    cpu_capacity: 4
    memory_gb: 16
    workload_type: "mixed"
    peak_hours: [9, 10, 11, 15, 16, 17]
    
    # Test environment characteristics
    workload:
      base_cpu_utilization: 15.0
      base_memory_utilization: 0.4
      base_io_response_time: 10.0
      base_cf_service_time: 20.0
      
    # Variable workload patterns
    test_patterns:
      load_testing:
        enabled: true
        frequency: "daily"
        duration: 60  # 1 hour
        cpu_spike_factor: 4.0
        memory_spike_factor: 2.0
      stress_testing:
        enabled: true
        frequency: "weekly"
        duration: 30  # 30 minutes
        cpu_spike_factor: 5.0
        memory_spike_factor: 3.0
        
# Global LPAR settings
global_settings:
  sysplex_name: "${SYSPLEX_NAME:-SYSPLEX01}"
  
  # Coupling facility configuration
  coupling_facility:
    links:
      - name: "CF01"
        base_service_time: 25.0
        max_service_time: 200.0
      - name: "CF02"
        base_service_time: 30.0
        max_service_time: 250.0
      - name: "CF03"
        base_service_time: 20.0
        max_service_time: 180.0
      - name: "CF04"
        base_service_time: 35.0
        max_service_time: 300.0
        
  # Message processing configuration
  message_processing:
    queue_types:
      - name: "CICS"
        base_processing_rate: 5000
        base_queue_depth: 50
      - name: "IMS"
        base_processing_rate: 3000
        base_queue_depth: 30
      - name: "MQ"
        base_processing_rate: 2000
        base_queue_depth: 20
      - name: "BATCH"
        base_processing_rate: 500
        base_queue_depth: 10
        
  # Performance variation settings
  variation:
    daily_cycle_amplitude: 0.3
    weekly_cycle_amplitude: 0.2
    monthly_cycle_amplitude: 0.1
    random_noise_factor: 0.1
    correlation_factor: 0.8
    
  # Seasonal patterns
  seasonal:
    enabled: true
    patterns:
      - name: "year_end_processing"
        start_month: 12
        start_day: 20
        end_month: 1
        end_day: 15
        cpu_factor: 1.5
        memory_factor: 1.3
        io_factor: 1.4
      - name: "quarterly_reporting"
        months: [3, 6, 9, 12]
        start_day: 25
        end_day: 5  # Next month
        cpu_factor: 1.3
        memory_factor: 1.2
        io_factor: 1.3
```

### Custom LPAR Configuration

Create environment-specific LPAR configurations:

```yaml
# config/lpars-production.yaml
lpars:
  - name: "PROD01"
    cpu_capacity: 32
    memory_gb: 128
    workload_type: "online"
    peak_hours: [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    
  - name: "PROD02"
    cpu_capacity: 32
    memory_gb: 128
    workload_type: "online"
    peak_hours: [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    
  - name: "PROD03"
    cpu_capacity: 24
    memory_gb: 96
    workload_type: "online"
    peak_hours: [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    
  - name: "BATCH01"
    cpu_capacity: 16
    memory_gb: 64
    workload_type: "batch"
    peak_hours: [20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6]
    
  - name: "BATCH02"
    cpu_capacity: 16
    memory_gb: 64
    workload_type: "batch"
    peak_hours: [20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6]
    
  - name: "DEV01"
    cpu_capacity: 8
    memory_gb: 32
    workload_type: "mixed"
    peak_hours: [9, 10, 11, 12, 13, 14, 15, 16, 17]
    
  - name: "TEST01"
    cpu_capacity: 8
    memory_gb: 32
    workload_type: "mixed"
    peak_hours: [9, 10, 11, 12, 13, 14, 15, 16, 17]
```

---

## 💾 Storage Configuration

### MySQL Configuration

Create `config/mysql.yaml`:

```yaml
# MySQL configuration
mysql:
  # Connection settings
  connection:
    host: "${MYSQL_HOST:-localhost}"
    port: ${MYSQL_PORT:-3306}
    database: "${MYSQL_DATABASE:-rmf_monitoring}"
    user: "${MYSQL_USER:-rmf_user}"
    password: "${MYSQL_PASSWORD}"
    charset: "${MYSQL_CHARSET:-utf8mb4}"
    collation: "${MYSQL_COLLATION:-utf8mb4_unicode_ci}"
    
  # Connection pool settings
  pool:
    max_connections: ${MYSQL_MAX_CONNECTIONS:-100}
    min_connections: ${MYSQL_MIN_CONNECTIONS:-10}
    connection_timeout: ${MYSQL_CONNECTION_TIMEOUT:-5000}
    idle_timeout: 300000
    max_lifetime: 3600000
    validation_query: "SELECT 1"
    test_on_borrow: true
    test_on_return: false
    test_while_idle: true
    
  # Performance settings
  performance:
    isolation_level: "READ_COMMITTED"
    autocommit: true
    batch_size: 1000
    query_timeout: 30000
    
  # Table settings
  tables:
    engine: "InnoDB"
    charset: "utf8mb4"
    collation: "utf8mb4_unicode_ci"
    
    # Partitioning settings
    partitioning:
      enabled: true
      strategy: "range"
      column: "timestamp"
      interval: "month"
      retention_months: 3
      
  # Backup settings
  backup:
    enabled: true
    schedule: "0 2 * * *"  # Daily at 2 AM
    retention_days: 30
    compression: true
    
  # Monitoring
  monitoring:
    enabled: true
    slow_query_log: true
    slow_query_time: 2
    log_queries_not_using_indexes: true
```

### MongoDB Configuration

Create `config/mongodb.yaml`:

```yaml
# MongoDB configuration
mongodb:
  # Connection settings
  connection:
    host: "${MONGO_HOST:-localhost}"
    port: ${MONGO_PORT:-27017}
    database: "${MONGO_DATABASE:-rmf_monitoring}"
    username: "${MONGO_USERNAME:-rmf_user}"
    password: "${MONGO_PASSWORD}"
    auth_source: "${MONGO_AUTH_SOURCE:-admin}"
    replica_set: "${MONGO_REPLICA_SET:-}"
    
  # Connection pool settings
  pool:
    max_pool_size: ${MONGO_MAX_POOL_SIZE:-50}
    min_pool_size: ${MONGO_MIN_POOL_SIZE:-5}
    connection_timeout: ${MONGO_CONNECTION_TIMEOUT:-5000}
    server_selection_timeout: ${MONGO_SERVER_SELECTION_TIMEOUT:-5000}
    socket_timeout: 30000
    max_idle_time: 300000
    
  # Performance settings
  performance:
    retry_writes: true
    retry_reads: true
    read_preference: "secondaryPreferred"
    read_concern: "majority"
    write_concern:
      w: "majority"
      j: true
      wtimeout: 5000
      
  # Collection settings
  collections:
    # TTL settings for automatic cleanup
    ttl:
      cpu_metrics: 7776000      # 90 days
      memory_metrics: 7776000   # 90 days
      ldev_metrics: 7776000     # 90 days
      
    # Sharding settings
    sharding:
      enabled: false
      shard_key: "lpar"
      
    # Indexing settings
    indexing:
      background: true
      sparse: true
      
  # Aggregation settings
  aggregation:
    allow_disk_use: true
    cursor_timeout: 600000
    batch_size: 1000
    
  # Backup settings
  backup:
    enabled: true
    schedule: "0 3 * * *"  # Daily at 3 AM
    retention_days: 30
    compression: true
    
  # Monitoring
  monitoring:
    enabled: true
    profile_slow_operations: true
    slow_operation_threshold: 100
    log_level: "INFO"
```

### S3/MinIO Configuration

Create `config/s3.yaml`:

```yaml
# S3/MinIO configuration
s3:
  # Connection settings
  connection:
    endpoint_url: "${S3_ENDPOINT_URL:-http://localhost:9000}"
    access_key: "${S3_ACCESS_KEY:-minioadmin}"
    secret_key: "${S3_SECRET_KEY}"
    region: "${S3_REGION:-us-east-1}"
    bucket_name: "${S3_BUCKET_NAME:-rmf-metrics}"
    use_ssl: ${S3_USE_SSL:-false}
    signature_version: "${S3_SIGNATURE_VERSION:-s3v4}"
    addressing_style: "${S3_ADDRESSING_STYLE:-virtual}"
    
  # Performance settings
  performance:
    max_pool_connections: ${S3_MAX_POOL_CONNECTIONS:-50}
    max_attempts: 3
    retry_mode: "adaptive"
    connect_timeout: 60
    read_timeout: 60
    
  # Storage settings
  storage:
    multipart_threshold: 67108864  # 64MB
    multipart_chunk_size: 8388608  # 8MB
    max_concurrency: 10
    use_threads: true
    
  # Lifecycle policies
  lifecycle:
    rules:
      - id: "metrics_retention"
        status: "Enabled"
        prefix: "metrics/"
        expiration_days: 90
        noncurrent_version_expiration_days: 30
        
      - id: "archive_retention"
        status: "Enabled"
        prefix: "archive/"
        transitions:
          - days: 30
            storage_class: "GLACIER"
        expiration_days: 2555  # 7 years
        
      - id: "exports_cleanup"
        status: "Enabled"
        prefix: "exports/"
        expiration_days: 7
        
  # Compression settings
  compression:
    enabled: true
    algorithm: "gzip"
    level: 6
    
  # Backup settings
  backup:
    enabled: true
    schedule: "0 4 * * *"  # Daily at 4 AM
    retention_days: 30
    cross_region_replication: false
    
  # Monitoring
  monitoring:
    enabled: true
    metrics_enabled: true
    request_metrics: true
    inventory_enabled: false
```

---

## 📊 Monitoring Configuration

### Prometheus Configuration

Create `config/prometheus.yaml`:

```yaml
# Prometheus configuration
prometheus:
  # Global settings
  global:
    scrape_interval: "${PROMETHEUS_SCRAPE_INTERVAL:-15s}"
    evaluation_interval: "${PROMETHEUS_EVALUATION_INTERVAL:-15s}"
    scrape_timeout: "${PROMETHEUS_SCRAPE_TIMEOUT:-10s}"
    
  # Scrape configurations
  scrape_configs:
    - job_name: "rmf-simulator"
      static_configs:
        - targets: ["rmf-simulator:8000"]
      metrics_path: "/metrics"
      scrape_interval: "15s"
      scrape_timeout: "10s"
      
    - job_name: "mysql-exporter"
      static_configs:
        - targets: ["mysql-exporter:9104"]
      scrape_interval: "30s"
      
    - job_name: "mongodb-exporter"
      static_configs:
        - targets: ["mongodb-exporter:9216"]
      scrape_interval: "30s"
      
    - job_name: "minio-exporter"
      static_configs:
        - targets: ["minio:9000"]
      metrics_path: "/minio/v2/metrics/cluster"
      scrape_interval: "30s"
      
  # Rule files
  rule_files:
    - "/etc/prometheus/rules/*.yml"
    
  # Alerting configuration
  alerting:
    alertmanagers:
      - static_configs:
          - targets: ["alertmanager:9093"]
        timeout: "10s"
        api_version: "v2"
        
  # Storage settings
  storage:
    tsdb:
      retention:
        time: "${PROMETHEUS_RETENTION_TIME:-30d}"
        size: "${PROMETHEUS_RETENTION_SIZE:-50GB}"
      min_block_duration: "2h"
      max_block_duration: "36h"
      
  # Remote write/read (optional)
  remote_write: []
  remote_read: []
  
  # Recording rules
  recording_rules:
    - name: "rmf_aggregated_metrics"
      interval: "30s"
      rules:
        - record: "rmf:cpu_utilization:avg"
          expr: "avg(rmf_cpu_utilization_percent) by (sysplex, lpar)"
        - record: "rmf:memory_utilization:avg"
          expr: "avg(rmf_memory_usage_bytes) by (sysplex, lpar, memory_type)"
        - record: "rmf:io_response_time:p95"
          expr: "histogram_quantile(0.95, rate(rmf_ldev_response_time_seconds_bucket[5m]))"
```

### Grafana Configuration

Create `config/grafana.yaml`:

```yaml
# Grafana configuration
grafana:
  # Server settings
  server:
    protocol: "http"
    http_port: 3000
    domain: "${GRAFANA_DOMAIN:-localhost}"
    root_url: "${GRAFANA_ROOT_URL:-http://localhost:3000}"
    
  # Security settings
  security:
    admin_user: "${GRAFANA_ADMIN_USER:-admin}"
    admin_password: "${GRAFANA_ADMIN_PASSWORD:-admin}"
    secret_key: "${GRAFANA_SECRET_KEY:-}"
    
  # Database settings
  database:
    type: "sqlite3"
    path: "/var/lib/grafana/grafana.db"
    
  # Authentication
  auth:
    anonymous:
      enabled: false
    github:
      enabled: false
    google:
      enabled: false
      
  # Dashboard settings
  dashboards:
    default_home_dashboard_path: "/var/lib/grafana/dashboards/rmf-overview.json"
    
  # Data source settings
  datasources:
    - name: "Prometheus"
      type: "prometheus"
      url: "http://prometheus:9090"
      access: "proxy"
      isDefault: true
      jsonData:
        timeInterval: "30s"
        httpMethod: "POST"
        
  # Alerting settings
  alerting:
    enabled: true
    execute_alerts: true
    
  # Plugin settings
  plugins:
    - grafana-clock-panel
    - grafana-simple-json-datasource
    - grafana-worldmap-panel
    
  # SMTP settings
  smtp:
    enabled: false
    host: "${SMTP_HOST:-localhost:587}"
    user: "${SMTP_USER:-}"
    password: "${SMTP_PASSWORD:-}"
    from_address: "${SMTP_FROM:-grafana@localhost}"
    from# Configuration Guide

This guide covers all configuration options for the RMF Monitor III Data Simulator, including environment variables, configuration files, and deployment-specific settings.

## 📋 Table of Contents

1. [Environment Variables](#environment-variables)
2. [Configuration Files](#configuration-files)
3. [LPAR Configuration](#lpar-configuration)
4. [Storage Configuration](#storage-configuration)
5. [Monitoring Configuration](#monitoring-configuration)
6. [Security Configuration](#security-configuration)
7. [Performance Tuning](#performance-tuning)
8. [Deployment-Specific Configuration](#deployment-specific-configuration)

---

## 🌍 Environment Variables

### Application Configuration

```bash
# Core Application Settings
LOG_LEVEL=INFO                          # Logging level: DEBUG, INFO, WARNING, ERROR
PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc_dir
ENVIRONMENT=production                  # Environment: development, staging, production
APP_NAME="RMF Monitor III Data Simulator"
APP_VERSION=1.0.0
DEBUG=false                            # Enable debug mode

# Server Configuration
HOST=0.0.0.0                          # Server host
PORT=8000                             # Server port
WORKERS=4                             # Number of worker processes
RELOAD=false                          # Auto-reload on code changes (development only)

# Simulation Configuration
SIMULATION_INTERVAL=15                # Metric generation interval in seconds
SYSPLEX_NAME=SYSPLEX01               # Default sysplex name
BATCH_SIZE=50                        # Metrics batch size for storage
FLUSH_INTERVAL=60                    # Batch flush interval in seconds
```

### Database Configuration

#### MySQL Configuration

```bash
# MySQL Database Settings
MYSQL_HOST=localhost                  # MySQL server host
MYSQL_PORT=3306                      # MySQL server port
MYSQL_DATABASE=rmf_monitoring        # Database name
MYSQL_USER=rmf_user                  # Database username
MYSQL_PASSWORD=secure_password       # Database password
MYSQL_ROOT_PASSWORD=root_password    # Root password
MYSQL_CONNECTION_TIMEOUT=5000        # Connection timeout in milliseconds
MYSQL_MAX_CONNECTIONS=100            # Maximum connection pool size
MYSQL_MIN_CONNECTIONS=10             # Minimum connection pool size
MYSQL_CHARSET=utf8mb4               # Character set
MYSQL_COLLATION=utf8mb4_unicode_ci  # Collation
```

#### MongoDB Configuration

```bash
# MongoDB Database Settings
MONGO_HOST=localhost               # MongoDB server host
MONGO_PORT=27017                   # MongoDB server port
MONGO_DATABASE=rmf_monitoring
MONGO_USERNAME=rmf_user
MONGO_PASSWORD=rmf_password
MONGO_AUTH_SOURCE=rmf_monitoring
```

#### S3/MinIO Database Settings

```bash
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY=rmf_user
S3_SECRET_KEY=rmf_password123
S3_BUCKET_NAME=rmf-metrics
S3_REGION=us-east-1
S3_USE_SSL=false
```