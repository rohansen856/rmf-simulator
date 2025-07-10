# API Documentation

The RMF Monitor III Data Simulator provides a comprehensive REST API for interacting with the mainframe metrics simulation system.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. For production deployments, consider implementing:
- API key authentication
- JWT tokens
- OAuth2 integration

## API Endpoints

### Health Check Endpoints

#### GET /health
Check the health status of the simulator service.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200`: Service is healthy
- `503`: Service is unhealthy

---

#### GET /ready
Check if the service is ready to accept requests.

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200`: Service is ready
- `503`: Service is not ready

---

#### GET /startup
Check if the service has completed startup procedures.

**Response:**
```json
{
  "status": "started",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200`: Service has started
- `503`: Service is still starting

---

### System Information Endpoints

#### GET /
Get basic system information and available endpoints.

**Response:**
```json
{
  "name": "RMF Monitor III Data Simulator",
  "version": "1.0.0",
  "sysplex": "SYSPLEX01",
  "lpars": ["PROD01", "PROD02", "BATCH01", "TEST01"],
  "metrics_endpoint": "/metrics",
  "health_endpoint": "/health"
}
```

---

#### GET /system-info
Get detailed system information including LPAR configurations and current status.

**Response:**
```json
{
  "sysplex": "SYSPLEX01",
  "timestamp": "2024-01-15T10:30:00Z",
  "uptime_seconds": 3600,
  "lpars": [
    {
      "name": "PROD01",
      "workload_type": "online",
      "cpu_capacity": 16,
      "memory_gb": 64,
      "peak_hours": [8, 9, 10, 14, 15, 16],
      "current_load_factor": 1.4,
      "is_peak_hour": true
    },
    {
      "name": "PROD02",
      "workload_type": "online",
      "cpu_capacity": 12,
      "memory_gb": 48,
      "peak_hours": [8, 9, 10, 14, 15, 16],
      "current_load_factor": 1.2,
      "is_peak_hour": true
    },
    {
      "name": "BATCH01",
      "workload_type": "batch",
      "cpu_capacity": 8,
      "memory_gb": 32,
      "peak_hours": [22, 23, 0, 1, 2, 3, 4, 5],
      "current_load_factor": 0.3,
      "is_peak_hour": false
    },
    {
      "name": "TEST01",
      "workload_type": "mixed",
      "cpu_capacity": 4,
      "memory_gb": 16,
      "peak_hours": [9, 10, 11, 15, 16, 17],
      "current_load_factor": 0.8,
      "is_peak_hour": false
    }
  ]
}
```

---

### Metrics Endpoints

#### GET /metrics
Get Prometheus-formatted metrics for all simulated components.

**Response Format:** Prometheus text format

**Response Example:**
```
# HELP rmf_cpu_utilization_percent CPU utilization percentage
# TYPE rmf_cpu_utilization_percent gauge
rmf_cpu_utilization_percent{sysplex="SYSPLEX01",lpar="PROD01",cpu_type="general_purpose"} 75.5
rmf_cpu_utilization_percent{sysplex="SYSPLEX01",lpar="PROD01",cpu_type="ziip"} 45.3
rmf_cpu_utilization_percent{sysplex="SYSPLEX01",lpar="PROD01",cpu_type="zaap"} 31.8

# HELP rmf_memory_usage_bytes Memory usage in bytes
# TYPE rmf_memory_usage_bytes gauge
rmf_memory_usage_bytes{sysplex="SYSPLEX01",lpar="PROD01",memory_type="real_storage"} 51539607552
rmf_memory_usage_bytes{sysplex="SYSPLEX01",lpar="PROD01",memory_type="virtual_storage"} 274877906944
rmf_memory_usage_bytes{sysplex="SYSPLEX01",lpar="PROD01",memory_type="csa"} 419430400

# HELP rmf_ldev_response_time_seconds LDEV response time in seconds
# TYPE rmf_ldev_response_time_seconds histogram
rmf_ldev_response_time_seconds_bucket{sysplex="SYSPLEX01",lpar="PROD01",device_type="3390",le="0.001"} 0
rmf_ldev_response_time_seconds_bucket{sysplex="SYSPLEX01",lpar="PROD01",device_type="3390",le="0.005"} 0
rmf_ldev_response_time_seconds_bucket{sysplex="SYSPLEX01",lpar="PROD01",device_type="3390",le="0.01"} 15
rmf_ldev_response_time_seconds_bucket{sysplex="SYSPLEX01",lpar="PROD01",device_type="3390",le="0.025"} 45
rmf_ldev_response_time_seconds_bucket{sysplex="SYSPLEX01",lpar="PROD01",device_type="3390",le="0.05"} 78
rmf_ldev_response_time_seconds_bucket{sysplex="SYSPLEX01",lpar="PROD01",device_type="3390",le="0.1"} 95
rmf_ldev_response_time_seconds_bucket{sysplex="SYSPLEX01",lpar="PROD01",device_type="3390",le="0.25"} 100
rmf_ldev_response_time_seconds_bucket{sysplex="SYSPLEX01",lpar="PROD01",device_type="3390",le="0.5"} 100
rmf_ldev_response_time_seconds_bucket{sysplex="SYSPLEX01",lpar="PROD01",device_type="3390",le="1.0"} 100
rmf_ldev_response_time_seconds_bucket{sysplex="SYSPLEX01",lpar="PROD01",device_type="3390",le="+Inf"} 100
rmf_ldev_response_time_seconds_count{sysplex="SYSPLEX01",lpar="PROD01",device_type="3390"} 100
rmf_ldev_response_time_seconds_sum{sysplex="SYSPLEX01",lpar="PROD01",device_type="3390"} 1.245
```

**Content-Type:** `text/plain; version=0.0.4; charset=utf-8`

---

## Metric Categories

### CPU Metrics

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `rmf_cpu_utilization_percent` | Gauge | CPU utilization percentage | `sysplex`, `lpar`, `cpu_type` |

**CPU Types:**
- `general_purpose`: General purpose processors
- `ziip`: System z Integrated Information Processor
- `zaap`: System z Application Assist Processor

### Memory Metrics

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `rmf_memory_usage_bytes` | Gauge | Memory usage in bytes | `sysplex`, `lpar`, `memory_type` |

**Memory Types:**
- `real_storage`: Physical memory usage
- `virtual_storage`: Virtual memory usage
- `csa`: Common Service Area usage

### LDEV Metrics

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `rmf_ldev_response_time_seconds` | Histogram | LDEV response time in seconds | `sysplex`, `lpar`, `device_type` |
| `rmf_ldev_utilization_percent` | Gauge | LDEV utilization percentage | `sysplex`, `lpar`, `device_id` |

**Device Types:**
- `3390`: IBM 3390 disk storage
- `flashcopy`: FlashCopy operations
- `tape`: Tape storage devices

### Coupling Facility Metrics

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `rmf_clpr_service_time_microseconds` | Histogram | Coupling facility service time | `sysplex`, `lpar`, `cf_link` |
| `rmf_clpr_request_rate` | Gauge | Coupling facility request rate | `sysplex`, `lpar`, `cf_link`, `request_type` |

**Request Types:**
- `synchronous`: Synchronous CF requests
- `asynchronous`: Asynchronous CF requests

### Message Processing Metrics

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `rmf_mpb_processing_rate` | Gauge | Message processing rate | `sysplex`, `lpar`, `queue_type` |
| `rmf_mpb_queue_depth` | Gauge | Message queue depth | `sysplex`, `lpar`, `queue_type` |

**Queue Types:**
- `CICS`: CICS transaction queues
- `IMS`: IMS message queues
- `MQ`: MQ message queues  
- `BATCH`: Batch job queues

### Port Metrics

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `rmf_ports_utilization_percent` | Gauge | Port utilization percentage | `sysplex`, `lpar`, `port_type`, `port_id` |
| `rmf_ports_throughput_mbps` | Gauge | Port throughput in MB/s | `sysplex`, `lpar`, `port_type`, `port_id` |

**Port Types:**
- `OSA`: Open Systems Adapter
- `Hipersocket`: HiperSocket connections
- `FICON`: Fibre Connection

### Volume Metrics

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `rmf_volumes_utilization_percent` | Gauge | Volume utilization percentage | `sysplex`, `lpar`, `volume_type`, `volume_id` |
| `rmf_volumes_iops` | Gauge | Volume IOPS | `sysplex`, `lpar`, `volume_type`, `volume_id` |

**Volume Types:**
- `SYSRES`: System residence volumes
- `WORK`: Work volumes
- `USER`: User data volumes
- `TEMP`: Temporary volumes

## Error Handling

### Error Response Format

All API errors follow a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "additional": "context information"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/endpoint"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

### Common Error Codes

| Error Code | Description |
|------------|-------------|
| `INVALID_PARAMETER` | Invalid request parameter |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `INTERNAL_ERROR` | Internal server error |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable |

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default limit**: 100 requests per minute per IP
- **Burst limit**: 10 requests per second
- **Headers**: Rate limit information in response headers

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

## Caching

### Cache Headers

Responses include appropriate caching headers:

```
Cache-Control: max-age=15
ETag: "abc123"
Last-Modified: Mon, 15 Jan 2024 10:30:00 GMT
```

### Cache Strategy

- **Metrics endpoint**: 15-second cache
- **System info**: 60-second cache
- **Health checks**: No cache

## WebSocket Support

For real-time metric streaming, the API supports WebSocket connections:

### WebSocket Endpoint

```
ws://localhost:8000/ws/metrics
```

### WebSocket Messages

**Connection Message:**
```json
{
  "type": "connection",
  "status": "connected",
  "client_id": "abc123"
}
```

**Metrics Message:**
```json
{
  "type": "metrics",
  "timestamp": "2024-01-15T10:30:00Z",
  "sysplex": "SYSPLEX01",
  "lpar": "PROD01",
  "metrics": {
    "cpu_utilization": {
      "general_purpose": 75.5,
      "ziip": 45.3,
      "zaap": 31.8
    },
    "memory_usage": {
      "real_storage": 51539607552,
      "virtual_storage": 274877906944,
      "csa": 419430400
    }
  }
}
```

## Client Libraries

### Python Client

```python
import requests
import json

class RMFSimulatorClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_health(self):
        """Get health status"""
        response = self.session.get(f"{self.base_url}/health")
        return response.json()
    
    def get_system_info(self):
        """Get system information"""
        response = self.session.get(f"{self.base_url}/system-info")
        return response.json()
    
    def get_metrics(self):
        """Get Prometheus metrics"""
        response = self.session.get(f"{self.base_url}/metrics")
        return response.text

# Usage
client = RMFSimulatorClient()
health = client.get_health()
system_info = client.get_system_info()
metrics = client.get_metrics()
```

### JavaScript Client

```javascript
class RMFSimulatorClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async getHealth() {
        const response = await fetch(`${this.baseUrl}/health`);
        return response.json();
    }
    
    async getSystemInfo() {
        const response = await fetch(`${this.baseUrl}/system-info`);
        return response.json();
    }
    
    async getMetrics() {
        const response = await fetch(`${this.baseUrl}/metrics`);
        return response.text();
    }
    
    // WebSocket connection
    connectWebSocket() {
        const ws = new WebSocket(`ws://${this.baseUrl.replace('http://', '')}/ws/metrics`);
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Received metrics:', data);
        };
        
        return ws;
    }
}

// Usage
const client = new RMFSimulatorClient();
const health = await client.getHealth();
const systemInfo = await client.getSystemInfo();
const ws = client.connectWebSocket();
```

## OpenAPI Specification

The complete OpenAPI specification is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# System information
curl http://localhost:8000/system-info

# Prometheus metrics
curl http://localhost:8000/metrics

# Pretty-print JSON responses
curl -s http://localhost:8000/system-info | jq .
```

### Using HTTPie

```bash
# Health check
http GET localhost:8000/health

# System information
http GET localhost:8000/system-info

# Metrics with headers
http GET localhost:8000/metrics Accept:text/plain
```

### Using Postman

Import the OpenAPI specification into Postman:
1. Open Postman
2. Import → Link → http://localhost:8000/openapi.json
3. Create a new environment with `base_url = http://localhost:8000`

## Performance Considerations

### Response Times

| Endpoint | Expected Response Time |
|----------|------------------------|
| `/health` | < 10ms |
| `/ready` | < 10ms |
| `/system-info` | < 50ms |
| `/metrics` | < 200ms |

### Concurrent Requests

The API supports high concurrency:
- **Max connections**: 1000 concurrent connections
- **Worker processes**: Auto-detected based on CPU cores
- **Async processing**: All endpoints are async-capable

### Memory Usage

- **Base memory**: ~100MB
- **Per connection**: ~1MB
- **Metrics generation**: ~50MB working set

## Security Considerations

### Current Implementation

- No authentication required
- CORS enabled for all origins
- No rate limiting by default
- HTTP only (no HTTPS)

### Production Recommendations

1. **Enable HTTPS**: Use TLS/SSL certificates
2. **Implement authentication**: API keys or OAuth2
3. **Restrict CORS**: Limit allowed origins
4. **Add rate limiting**: Prevent abuse
5. **Input validation**: Sanitize all inputs
6. **Logging**: Comprehensive security logging

### Security Headers

Consider adding security headers:

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
```