# Deployment Guide

This guide covers deployment options for the RMF Monitor III Data Simulator across different environments.

## 🚀 Deployment Options

### 1. Docker Compose (Recommended for Development/Testing)
### 2. Kubernetes (Production)
### 3. Local Development
### 4. Cloud Platforms

---

## 🐳 Docker Compose Deployment

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ RAM
- 50GB+ storage

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/rmf-monitor-simulator.git
cd rmf-monitor-simulator

# Start all services
docker-compose up -d

# Verify deployment
docker-compose ps
```

### Configuration

Create a `.env` file for environment-specific settings:

```bash
# .env file
COMPOSE_PROJECT_NAME=rmf-simulator

# Application Configuration
LOG_LEVEL=INFO
PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc_dir

# MySQL Configuration
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_DATABASE=rmf_monitoring
MYSQL_USER=rmf_user
MYSQL_PASSWORD=your_secure_password
MYSQL_ROOT_PASSWORD=your_root_password

# MongoDB Configuration
MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_DATABASE=rmf_monitoring
MONGO_USERNAME=rmf_user
MONGO_PASSWORD=your_secure_password

# MinIO Configuration
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=your_secure_password
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY=rmf_user
S3_SECRET_KEY=your_secure_password
S3_BUCKET_NAME=rmf-metrics

# Monitoring Configuration
GRAFANA_ADMIN_PASSWORD=your_secure_password
```

### Service Access

| Service | URL | Default Credentials |
|---------|-----|-------------------|
| Simulator API | http://localhost:8000 | None |
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | None |
| MinIO Console | http://localhost:9001 | minioadmin/minioadmin123 |
| MySQL | localhost:3306 | root/root_password |
| MongoDB | localhost:27017 | admin/admin_password |

### Health Checks

```bash
# Check all services
docker-compose ps

# Check specific service logs
docker-compose logs rmf-simulator

# Check service health
curl http://localhost:8000/health
```

### Scaling Services

```bash
# Scale simulator instances
docker-compose up -d --scale rmf-simulator=3

# Scale with custom configuration
docker-compose -f docker-compose.yml -f docker-compose.scale.yml up -d
```

### Backup and Restore

```bash
# Backup volumes
docker-compose exec mysql mysqldump -u root -p rmf_monitoring > backup.sql
docker-compose exec mongodb mongodump --db rmf_monitoring --out /backup/

# Restore volumes
docker-compose exec mysql mysql -u root -p rmf_monitoring < backup.sql
docker-compose exec mongodb mongorestore --db rmf_monitoring /backup/rmf_monitoring/
```

---

## ☸️ Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured
- Helm (optional, for easier management)
- 16GB+ RAM across cluster
- 100GB+ storage

### Namespace Setup

```bash
# Create namespace
kubectl create namespace rmf-monitoring

# Set default namespace
kubectl config set-context --current --namespace=rmf-monitoring
```

### Deploy with Manifests

```bash
# Deploy in order
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmaps.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/persistentvolumes.yaml
kubectl apply -f k8s/mysql.yaml
kubectl apply -f k8s/mongodb.yaml
kubectl apply -f k8s/minio.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/services.yaml
kubectl apply -f k8s/ingress.yaml

# Verify deployment
kubectl get all -n rmf-monitoring
```

### Deploy with Helm

```bash
# Add custom Helm chart repository
helm repo add rmf-simulator https://your-org.github.io/rmf-simulator-charts

# Install with custom values
helm install rmf-simulator rmf-simulator/rmf-simulator \
  --namespace rmf-monitoring \
  --create-namespace \
  --values values.yaml
```

### Helm Values Configuration

```yaml
# values.yaml
global:
  storageClass: "fast-ssd"
  imageRegistry: "your-registry.com"

simulator:
  replicaCount: 3
  image:
    repository: rmf-simulator
    tag: "latest"
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 500m
      memory: 512Mi

mysql:
  enabled: true
  persistence:
    size: 50Gi
  resources:
    limits:
      cpu: 2000m
      memory: 4Gi

mongodb:
  enabled: true
  persistence:
    size: 100Gi
  resources:
    limits:
      cpu: 2000m
      memory: 4Gi

minio:
  enabled: true
  persistence:
    size: 200Gi
  resources:
    limits:
      cpu: 1000m
      memory: 2Gi

prometheus:
  enabled: true
  retention: "30d"
  persistence:
    size: 50Gi

grafana:
  enabled: true
  adminPassword: "your-secure-password"
  persistence:
    size: 10Gi

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: rmf-simulator.your-domain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: rmf-simulator-tls
      hosts:
        - rmf-simulator.your-domain.com
```

### Monitoring Deployment

```bash
# Check pod status
kubectl get pods -n rmf-monitoring

# Check service status
kubectl get svc -n rmf-monitoring

# Check logs
kubectl logs -f deployment/rmf-simulator -n rmf-monitoring

# Check events
kubectl get events -n rmf-monitoring --sort-by=.metadata.creationTimestamp
```

### Scaling

```bash
# Scale simulator
kubectl scale deployment rmf-simulator --replicas=5 -n rmf-monitoring

# Enable auto-scaling
kubectl apply -f k8s/hpa.yaml

# Check HPA status
kubectl get hpa -n rmf-monitoring
```

### Secrets Management

```bash
# Create secrets
kubectl create secret generic rmf-secrets \
  --from-literal=mysql-password=your-password \
  --from-literal=mongodb-password=your-password \
  --from-literal=minio-password=your-password \
  -n rmf-monitoring

# Use external secret management
kubectl apply -f k8s/external-secrets.yaml
```

---

## 🌐 Cloud Platform Deployment

### AWS Deployment

#### EKS Cluster Setup

```bash
# Create EKS cluster
eksctl create cluster --name rmf-simulator-cluster \
  --region us-west-2 \
  --nodegroup-name rmf-nodes \
  --node-type m5.xlarge \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 6 \
  --ssh-access \
  --ssh-public-key my-key

# Configure kubectl
aws eks update-kubeconfig --region us-west-2 --name rmf-simulator-cluster
```

#### AWS Load Balancer Controller

```bash
# Install AWS Load Balancer Controller
kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller//crds?ref=master"

helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=rmf-simulator-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller
```

#### RDS Integration

```yaml
# Use AWS RDS for MySQL
apiVersion: v1
kind: Secret
metadata:
  name: rds-secret
type: Opaque
data:
  host: <base64-encoded-rds-endpoint>
  username: <base64-encoded-username>
  password: <base64-encoded-password>
  database: <base64-encoded-database>
```

#### S3 Integration

```yaml
# Use AWS S3 instead of MinIO
apiVersion: v1
kind: ConfigMap
metadata:
  name: s3-config
data:
  S3_ENDPOINT_URL: ""
  S3_REGION: "us-west-2"
  S3_BUCKET_NAME: "rmf-metrics-bucket"
```

### Azure Deployment

#### AKS Cluster Setup

```bash
# Create resource group
az group create --name rmf-simulator-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group rmf-simulator-rg \
  --name rmf-simulator-cluster \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group rmf-simulator-rg --name rmf-simulator-cluster
```

#### Azure Database Integration

```yaml
# Use Azure Database for MySQL
apiVersion: v1
kind: Secret
metadata:
  name: azure-mysql-secret
type: Opaque
data:
  host: <azure-mysql-server>.mysql.database.azure.com
  username: <username>@<server-name>
  password: <password>
```

### Google Cloud Platform

#### GKE Cluster Setup

```bash
# Create GKE cluster
gcloud container clusters create rmf-simulator-cluster \
  --zone us-central1-a \
  --machine-type n1-standard-4 \
  --num-nodes 3 \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 6

# Get credentials
gcloud container clusters get-credentials rmf-simulator-cluster --zone us-central1-a
```

#### Cloud SQL Integration

```yaml
# Use Cloud SQL for MySQL
apiVersion: v1
kind: Secret
metadata:
  name: cloudsql-secret
type: Opaque
data:
  host: <cloudsql-instance-ip>
  username: <username>
  password: <password>
```

---

## 🔧 Configuration Management

### Environment Variables

```bash
# Application Configuration
export LOG_LEVEL=INFO
export PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc_dir

# Database Configuration
export MYSQL_HOST=mysql
export MYSQL_PORT=3306
export MYSQL_DATABASE=rmf_monitoring
export MYSQL_USER=rmf_user
export MYSQL_PASSWORD=secure_password

# MongoDB Configuration
export MONGO_HOST=mongodb
export MONGO_PORT=27017
export MONGO_DATABASE=rmf_monitoring
export MONGO_USERNAME=rmf_user
export MONGO_PASSWORD=secure_password

# S3 Configuration
export S3_ENDPOINT_URL=http://minio:9000
export S3_ACCESS_KEY=rmf_user
export S3_SECRET_KEY=secure_password
export S3_BUCKET_NAME=rmf-metrics
```

### Configuration Files

#### Application Configuration

```yaml
# config/app.yaml
application:
  name: "RMF Monitor III Data Simulator"
  version: "1.0.0"
  debug: false
  log_level: "INFO"

simulator:
  update_interval: 15
  sysplex_name: "SYSPLEX01"
  batch_size: 50
  flush_interval: 60

storage:
  mysql:
    enabled: true
    host: "${MYSQL_HOST}"
    port: ${MYSQL_PORT}
    database: "${MYSQL_DATABASE}"
    user: "${MYSQL_USER}"
    password: "${MYSQL_PASSWORD}"
  
  mongodb:
    enabled: true
    host: "${MONGO_HOST}"
    port: ${MONGO_PORT}
    database: "${MONGO_DATABASE}"
    username: "${MONGO_USERNAME}"
    password: "${MONGO_PASSWORD}"
  
  s3:
    enabled: true
    endpoint_url: "${S3_ENDPOINT_URL}"
    access_key: "${S3_ACCESS_KEY}"
    secret_key: "${S3_SECRET_KEY}"
    bucket_name: "${S3_BUCKET_NAME}"
```

#### LPAR Configuration

```yaml
# config/lpars.yaml
lpars:
  - name: "PROD01"
    cpu_capacity: 16
    memory_gb: 64
    workload_type: "online"
    peak_hours: [8, 9, 10, 14, 15, 16]
    
  - name: "PROD02"
    cpu_capacity: 12
    memory_gb: 48
    workload_type: "online"
    peak_hours: [8, 9, 10, 14, 15, 16]
    
  - name: "BATCH01"
    cpu_capacity: 8
    memory_gb: 32
    workload_type: "batch"
    peak_hours: [22, 23, 0, 1, 2, 3, 4, 5]
    
  - name: "TEST01"
    cpu_capacity: 4
    memory_gb: 16
    workload_type: "mixed"
    peak_hours: [9, 10, 11, 15, 16, 17]
```

---

## 🔐 Security Configuration

### TLS/SSL Setup

#### Self-Signed Certificates

```bash
# Generate self-signed certificates
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Create Kubernetes secret
kubectl create secret tls rmf-simulator-tls --cert=cert.pem --key=key.pem -n rmf-monitoring
```

#### Let's Encrypt with Cert-Manager

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

### Authentication Setup

#### API Key Authentication

```python
# middleware/auth.py
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    api_key = os.getenv("API_KEY")
    if not api_key or credentials.credentials != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials
```

#### OAuth2 Integration

```yaml
# oauth2-proxy configuration
apiVersion: apps/v1
kind: Deployment
metadata:
  name: oauth2-proxy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: oauth2-proxy
  template:
    metadata:
      labels:
        app: oauth2-proxy
    spec:
      containers:
      - name: oauth2-proxy
        image: quay.io/oauth2-proxy/oauth2-proxy:latest
        args:
        - --provider=github
        - --email-domain=yourdomain.com
        - --upstream=http://rmf-simulator:8000
        - --http-address=0.0.0.0:4180
        env:
        - name: OAUTH2_PROXY_CLIENT_ID
          value: "your-github-client-id"
        - name: OAUTH2_PROXY_CLIENT_SECRET
          value: "your-github-client-secret"
        - name: OAUTH2_PROXY_COOKIE_SECRET
          value: "your-cookie-secret"
        ports:
        - containerPort: 4180
```

### Network Security

#### Network Policies

```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: rmf-simulator-network-policy
  namespace: rmf-monitoring
spec:
  podSelector:
    matchLabels:
      app: rmf-simulator
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    - podSelector:
        matchLabels:
          app: prometheus
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: mysql
    ports:
    - protocol: TCP
      port: 3306
  - to:
    - podSelector:
        matchLabels:
          app: mongodb
    ports:
    - protocol: TCP
      port: 27017
  - to:
    - podSelector:
        matchLabels:
          app: minio
    ports:
    - protocol: TCP
      port: 9000
```

#### Service Mesh with Istio

```yaml
# istio/virtual-service.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: rmf-simulator
  namespace: rmf-monitoring
spec:
  hosts:
  - rmf-simulator.yourdomain.com
  gateways:
  - rmf-simulator-gateway
  http:
  - match:
    - uri:
        prefix: /
    route:
    - destination:
        host: rmf-simulator.rmf-monitoring.svc.cluster.local
        port:
          number: 8000
    timeout: 30s
    retries:
      attempts: 3
      perTryTimeout: 10s
```

---

## 📊 Monitoring and Observability

### Prometheus Configuration

```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "/etc/prometheus/rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'rmf-simulator'
    static_configs:
      - targets: ['rmf-simulator:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
    scrape_timeout: 10s
    
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
      action: keep
      regex: true
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
      action: replace
      target_label: __metrics_path__
      regex: (.+)
    - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
      action: replace
      regex: ([^:]+)(?::\d+)?;(\d+)
      replacement: $1:$2
      target_label: __address__
```

### Grafana Dashboard Provisioning

```yaml
# grafana/provisioning/dashboards/dashboard.yaml
apiVersion: 1
providers:
  - name: 'RMF Dashboards'
    orgId: 1
    folder: 'RMF Monitor III'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
```

### Alerting Rules

```yaml
# prometheus/rules/rmf-alerts.yml
groups:
- name: rmf-simulator-alerts
  rules:
  - alert: RMFSimulatorDown
    expr: up{job="rmf-simulator"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "RMF Simulator is down"
      description: "RMF Simulator has been down for more than 1 minute"
      
  - alert: HighCPUUtilization
    expr: rmf_cpu_utilization_percent > 90
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU utilization on {{ $labels.lpar }}"
      description: "CPU utilization on {{ $labels.lpar }} has exceeded 90% for 5 minutes"
      
  - alert: HighMemoryUsage
    expr: (rmf_memory_usage_bytes{memory_type="real_storage"} / (64 * 1024 * 1024 * 1024)) * 100 > 85
    for: 3m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage on {{ $labels.lpar }}"
      description: "Memory usage on {{ $labels.lpar }} has exceeded 85% for 3 minutes"
      
  - alert: DatabaseConnectionError
    expr: increase(rmf_database_errors_total[5m]) > 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Database connection errors detected"
      description: "Database connection errors have been detected in the last 5 minutes"
```

### Logging Configuration

```yaml
# logging/fluent-bit.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
  namespace: rmf-monitoring
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush         1
        Log_Level     info
        Daemon        off
        Parsers_File  parsers.conf
        HTTP_Server   On
        HTTP_Listen   0.0.0.0
        HTTP_Port     2020
        
    [INPUT]
        Name              tail
        Path              /var/log/containers/rmf-simulator*.log
        Parser            docker
        Tag               kube.*
        Refresh_Interval  5
        
    [OUTPUT]
        Name  es
        Match *
        Host  elasticsearch
        Port  9200
        Index rmf-simulator-logs
        Type  _doc
```

---

## 📈 Performance Tuning

### Resource Allocation

#### CPU and Memory Limits

```yaml
# k8s/deployment.yaml
resources:
  requests:
    cpu: 500m
    memory: 1Gi
  limits:
    cpu: 2000m
    memory: 4Gi
```

#### JVM Tuning (if using Java components)

```yaml
env:
- name: JAVA_OPTS
  value: "-Xmx2g -Xms1g -XX:+UseG1GC -XX:MaxGCPauseMillis=200"
```

### Database Optimization

#### MySQL Configuration

```ini
# mysql/conf.d/my.cnf
[mysqld]
innodb_buffer_pool_size = 4G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2
query_cache_size = 128M
max_connections = 1000
slow_query_log = 1
long_query_time = 2
```

#### MongoDB Configuration

```yaml
# mongodb configuration
storage:
  wiredTiger:
    engineConfig:
      cacheSizeGB: 4
    collectionConfig:
      blockCompressor: snappy
    indexConfig:
      prefixCompression: true
      
replication:
  replSetName: "rmf-replica-set"
  
operationProfiling:
  slowOpThresholdMs: 100
  mode: slowOp
```

### Application Tuning

#### FastAPI Configuration

```python
# app/main.py
from fastapi import FastAPI
from uvicorn.config import Config
from uvicorn.server import Server

app = FastAPI(
    title="RMF Monitor III Data Simulator",
    description="Production-ready z/OS metrics simulator",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
)

# Configure uvicorn for production
if __name__ == "__main__":
    config = Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        workers=4,
        loop="uvloop",
        http="httptools",
        access_log=False,
        server_header=False,
        date_header=False,
    )
    server = Server(config)
    server.run()
```

---

## 🔄 Backup and Disaster Recovery

### Backup Strategy

#### Database Backups

```bash
# MySQL backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mysql"
mkdir -p $BACKUP_DIR

# Create backup
kubectl exec -n rmf-monitoring deployment/mysql -- \
  mysqldump -u root -p$MYSQL_ROOT_PASSWORD rmf_monitoring > \
  $BACKUP_DIR/rmf_monitoring_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/rmf_monitoring_$DATE.sql

# Upload to S3
aws s3 cp $BACKUP_DIR/rmf_monitoring_$DATE.sql.gz \
  s3://rmf-backups/mysql/rmf_monitoring_$DATE.sql.gz
```

```bash
# MongoDB backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mongodb"
mkdir -p $BACKUP_DIR

# Create backup
kubectl exec -n rmf-monitoring deployment/mongodb -- \
  mongodump --db rmf_monitoring --out $BACKUP_DIR/rmf_monitoring_$DATE

# Compress backup
tar -czf $BACKUP_DIR/rmf_monitoring_$DATE.tar.gz -C $BACKUP_DIR rmf_monitoring_$DATE

# Upload to S3
aws s3 cp $BACKUP_DIR/rmf_monitoring_$DATE.tar.gz \
  s3://rmf-backups/mongodb/rmf_monitoring_$DATE.tar.gz
```

#### Persistent Volume Backups

```yaml
# velero backup configuration
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: rmf-simulator-backup
  namespace: rmf-monitoring
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  template:
    includedNamespaces:
    - rmf-monitoring
    storageLocation: default
    ttl: 720h  # 30 days
    snapshotVolumes: true
```

### Disaster Recovery

#### Multi-Region Deployment

```yaml
# disaster-recovery/active-passive.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: rmf-simulator-dr
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/rmf-simulator
    targetRevision: HEAD
    path: k8s/dr
  destination:
    server: https://dr-cluster-api-server
    namespace: rmf-monitoring
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

#### Data Replication

```yaml
# mysql replication configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-master-config
data:
  my.cnf: |
    [mysqld]
    server-id = 1
    log-bin = mysql-bin
    binlog-format = ROW
    sync_binlog = 1
    innodb_flush_log_at_trx_commit = 1
    
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-slave-config
data:
  my.cnf: |
    [mysqld]
    server-id = 2
    relay-log = mysql-relay-bin
    read-only = 1
    super-read-only = 1
```

---

## 🚦 Health Checks and Monitoring

### Kubernetes Health Checks

```yaml
# Health check configuration
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
  successThreshold: 1

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
  successThreshold: 1

startupProbe:
  httpGet:
    path: /startup
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 30
  successThreshold: 1
```

### External Monitoring

#### Uptime Monitoring

```yaml
# uptime-kuma configuration
apiVersion: apps/v1
kind: Deployment
metadata:
  name: uptime-kuma
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: uptime-kuma
  template:
    metadata:
      labels:
        app: uptime-kuma
    spec:
      containers:
      - name: uptime-kuma
        image: louislam/uptime-kuma:latest
        ports:
        - containerPort: 3001
        volumeMounts:
        - name: uptime-kuma-data
          mountPath: /app/data
      volumes:
      - name: uptime-kuma-data
        persistentVolumeClaim:
          claimName: uptime-kuma-pvc
```

---

## 🔧 Troubleshooting

### Common Issues

#### Pod Startup Issues

```bash
# Check pod status
kubectl get pods -n rmf-monitoring

# Check pod logs
kubectl logs -f deployment/rmf-simulator -n rmf-monitoring

# Describe pod for events
kubectl describe pod <pod-name> -n rmf-monitoring

# Check resource usage
kubectl top pods -n rmf-monitoring
```

#### Database Connection Issues

```bash
# Test MySQL connection
kubectl exec -it deployment/mysql -n rmf-monitoring -- \
  mysql -u root -p -e "SELECT 1"

# Test MongoDB connection
kubectl exec -it deployment/mongodb -n rmf-monitoring -- \
  mongosh --eval "db.adminCommand('ping')"

# Check database logs
kubectl logs -f deployment/mysql -n rmf-monitoring
kubectl logs -f deployment/mongodb -n rmf-monitoring
```

#### Storage Issues

```bash
# Check persistent volumes
kubectl get pv,pvc -n rmf-monitoring

# Check storage usage
kubectl exec -it deployment/mysql -n rmf-monitoring -- \
  df -h

# Check MinIO status
kubectl logs -f deployment/minio -n rmf-monitoring
```

### Performance Issues

#### CPU and Memory

```bash
# Check resource usage
kubectl top pods -n rmf-monitoring
kubectl top nodes

# Check resource limits
kubectl describe deployment rmf-simulator -n rmf-monitoring

# Check HPA status
kubectl get hpa -n rmf-monitoring
```

#### Network Issues

```bash
# Check service endpoints
kubectl get endpoints -n rmf-monitoring

# Test service connectivity
kubectl exec -it deployment/rmf-simulator -n rmf-monitoring -- \
  curl http://mysql:3306

# Check ingress status
kubectl get ingress -n rmf-monitoring
kubectl describe ingress rmf-simulator -n rmf-monitoring
```

### Debug Commands

```bash
# Enter pod for debugging
kubectl exec -it deployment/rmf-simulator -n rmf-monitoring -- /bin/bash

# Port forward for local access
kubectl port-forward deployment/rmf-simulator 8000:8000 -n rmf-monitoring

# Check cluster events
kubectl get events -n rmf-monitoring --sort-by=.metadata.creationTimestamp

# Check cluster resources
kubectl describe node <node-name>
```

---

## 🔒 Security Hardening

### Container Security

```yaml
# Security context configuration
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
  allowPrivilegeEscalation: false
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: true
  seccompProfile:
    type: RuntimeDefault
```

### Pod Security Standards

```yaml
# Pod security policy
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: rmf-simulator-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

### Network Security

```yaml
# Ingress with TLS
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rmf-simulator-ingress
  namespace: rmf-monitoring
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - rmf-simulator.yourdomain.com
    secretName: rmf-simulator-tls
  rules:
  - host: rmf-simulator.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: rmf-simulator
            port:
              number: 8000
```

This comprehensive deployment guide covers all aspects of deploying the RMF Monitor III Data Simulator across different environments, from development to production-ready Kubernetes clusters with full security, monitoring, and disaster recovery capabilities.