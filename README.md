# RMF Monitor III Data Simulator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=flat&logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=flat&logo=Prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/grafana-%23F46800.svg?style=flat&logo=grafana&logoColor=white)](https://grafana.com/)

A production-ready z/OS mainframe metrics simulator that generates realistic IBM RMF (Resource Measurement Facility) Monitor III data with authentic workload patterns, comprehensive storage backends, and modern monitoring integration.

## 🚀 Key Features

### **Realistic Mainframe Simulation**
- **Authentic z/OS Metrics**: CPU (GP, zIIP, zAAP), memory (real/virtual/CSA), I/O, coupling facility, and network performance
- **Dynamic Workload Patterns**: Peak hours, batch processing windows, seasonal variations, and workload-specific behaviors
- **Multi-LPAR Support**: Simulates complete sysplex environments with different workload types (online, batch, mixed)
- **Proper Metric Relationships**: Interdependent metrics that mirror real mainframe behavior

### **Multi-Storage Architecture**
- **MySQL**: Relational storage with optimized indexing for analytical queries
- **MongoDB**: NoSQL document storage for flexible metric schemas and time-series data
- **S3-Compatible Storage**: MinIO integration for long-term archival and data lake scenarios
- **Prometheus**: Real-time metrics exposure with native integration

### **Production-Ready Deployment**
- **Containerized**: Docker and Kubernetes ready with comprehensive health checks
- **Scalable**: Horizontal pod autoscaling and load balancing support
- **Monitoring Stack**: Complete Prometheus + Grafana + Alertmanager integration
- **Security**: Non-root containers, RBAC, network policies, and secure defaults

### **Enterprise Features**
- **Comprehensive Alerting**: Performance threshold monitoring with multi-channel notifications
- **Data Lifecycle Management**: Automated cleanup, archival, and retention policies
- **Export Capabilities**: CSV export, backup creation, and data migration tools
- **Dashboard Templates**: Executive, operational, and troubleshooting views

## 📊 Supported Metrics

| Metric Category | Components | Description |
|---|---|---|
| **CPU** | GP, zIIP, zAAP processors | Utilization percentages with realistic specialty engine patterns |
| **Memory** | Real storage, virtual storage, CSA | Memory consumption across different storage types |
| **LDEV** | 3390, FlashCopy, Tape devices | Storage device utilization and response times |
| **CLPR** | Coupling facility links | Service times and request rates for CF connectivity |
| **MPB** | CICS, IMS, MQ, Batch queues | Message processing rates and queue depths |
| **Ports** | OSA, HiperSocket, FICON | Network port utilization and throughput |
| **Volumes** | SYSRES, WORK, USER, TEMP | Volume utilization and IOPS metrics |

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   Prometheus    │    │     Grafana     │
│   (Simulator)   │◄──►│   (Metrics)     │◄──►│   (Dashboard)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     MySQL       │    │    MongoDB      │    │  S3 (MinIO)     │
│  (Relational)   │    │  (Document)     │    │  (Object)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

The simulator generates metrics every 15 seconds, storing them simultaneously across multiple storage backends while exposing real-time metrics via Prometheus endpoints.

## 🚀 Quick Start

### Prerequisites
- **Docker** and **Docker Compose** installed
- **8GB+ RAM** recommended for full stack
- **Ports**: 3000 (Grafana), 8000 (Simulator), 9000 (MinIO), 9090 (Prometheus)

### One-Command Deployment
```bash
# Clone the repository
git clone https://github.com/your-org/rmf-monitor-simulator.git
cd rmf-monitor-simulator

# Start the complete stack
docker-compose up -d

# Verify all services are running
docker-compose ps
```

### Access Points
- **Simulator API**: http://localhost:8000
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin123)

## 📈 Monitoring & Dashboards

### Pre-built Dashboards
- **Executive Overview**: High-level system performance and availability
- **Operational Dashboard**: Real-time metrics for system operators
- **Troubleshooting View**: Detailed metrics for performance analysis
- **Capacity Planning**: Historical trends and growth projections

### Sample Queries
```promql
# CPU utilization across all LPARs
avg(rmf_cpu_utilization_percent{cpu_type="general_purpose"}) by (lpar)

# Memory usage percentage
(rmf_memory_usage_bytes{memory_type="real_storage"} / (64 * 1024 * 1024 * 1024)) * 100

# I/O response time 95th percentile
histogram_quantile(0.95, rate(rmf_ldev_response_time_seconds_bucket[5m]))
```

## 🔧 Configuration

### Environment Variables
```bash
# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=rmf_monitoring
MYSQL_USER=rmf_user
MYSQL_PASSWORD=rmf_password

# MongoDB Configuration
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DATABASE=rmf_monitoring
MONGO_USERNAME=rmf_user
MONGO_PASSWORD=rmf_password

# S3/MinIO Configuration
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=rmf_user
S3_SECRET_KEY=rmf_password123
S3_BUCKET_NAME=rmf-metrics
```

### LPAR Configuration
Modify `utils/config.py` to customize your mainframe environment:

```python
LPAR_CONFIGS = [
    LPARConfig("PROD01", 16, 64, "online", [8, 9, 10, 14, 15, 16]),
    LPARConfig("PROD02", 12, 48, "online", [8, 9, 10, 14, 15, 16]),
    LPARConfig("BATCH01", 8, 32, "batch", [22, 23, 0, 1, 2, 3, 4, 5]),
    LPARConfig("TEST01", 4, 16, "mixed", [9, 10, 11, 15, 16, 17]),
]
```

## 📚 API Documentation

### Health Endpoints
```bash
# Health check
GET /health

# Readiness probe
GET /ready

# Startup probe
GET /startup
```

### Metrics Endpoints
```bash
# Prometheus metrics
GET /metrics

# System information
GET /system-info

# Current LPAR status
GET /system-info
```

### Example Response
```json
{
  "sysplex": "SYSPLEX01",
  "timestamp": "2024-01-15T10:30:00Z",
  "lpars": [
    {
      "name": "PROD01",
      "workload_type": "online",
      "cpu_capacity": 16,
      "memory_gb": 64,
      "current_load_factor": 1.4,
      "is_peak_hour": true
    }
  ]
}
```

## 🔒 Security

### Container Security
- **Non-root execution**: All containers run as non-privileged users
- **Resource limits**: CPU and memory constraints applied
- **Network isolation**: Service-to-service communication only
- **Secret management**: Environment variable configuration

### Authentication
- **Database authentication**: Separate service accounts for each storage backend
- **API security**: Rate limiting and input validation
- **MinIO access**: IAM-based bucket policies

## 📦 Deployment Options

### Docker Compose (Development)
```bash
docker-compose up -d
```

### Kubernetes (Production)
```bash
kubectl apply -f k8s/
```

### Local Development
```bash
poetry install
poetry run uvicorn app.main:app --reload
```

## 📊 Performance & Scaling

### Resource Requirements
- **Minimum**: 4 CPU cores, 8GB RAM
- **Recommended**: 8 CPU cores, 16GB RAM
- **Storage**: 100GB+ for historical data

### Scaling Characteristics
- **Horizontal scaling**: Multiple simulator instances supported
- **Auto-scaling**: Kubernetes HPA based on CPU/memory metrics
- **Database scaling**: Read replicas and sharding support

## 🛠️ Troubleshooting

### Common Issues
1. **Port conflicts**: Check if ports 3000, 8000, 9000, 9090 are available
2. **Memory issues**: Ensure adequate RAM for all services
3. **Storage permissions**: Verify Docker volume permissions

### Debug Commands
```bash
# Check service logs
docker-compose logs rmf-simulator

# Verify metrics generation
curl http://localhost:8000/metrics

# Test database connectivity
docker-compose exec rmf-simulator python -c "from storage.mysql.service import DatabaseService; print(DatabaseService().get_connection_status())"
```

## 📈 Monitoring & Alerting

### Built-in Alerts
- **High CPU utilization** (>85% for 5 minutes)
- **Memory pressure** (>90% for 2 minutes)
- **I/O response time** (>50ms for 3 minutes)
- **Service unavailability** (health check failures)

### Custom Metrics
The simulator supports custom metric definitions and can be extended to simulate additional mainframe components.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:
- Setting up the development environment
- Running tests
- Submitting pull requests
- Code style guidelines

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/rmf-monitor-simulator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/rmf-monitor-simulator/discussions)

## 🙏 Acknowledgments

- IBM z/OS RMF documentation and metrics specifications
- Prometheus and Grafana communities
- FastAPI and modern Python ecosystem contributors

---

**Note**: This simulator is for educational and testing purposes. It generates synthetic data that resembles real mainframe metrics but should not be used for actual capacity planning or performance analysis of production systems.