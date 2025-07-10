# Contributing to RMF Monitor III Data Simulator

Thank you for considering contributing to the RMF Monitor III Data Simulator! This guide will help you set up your development environment and understand our contribution process.

## 🚀 Quick Start

### Prerequisites

**Required Software:**
- **Python 3.11+** with pip
- **Docker** and **Docker Compose**
- **Git**
- **Poetry** (Python dependency management)

**System Requirements:**
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 20GB free space
- **OS**: Linux, macOS, or Windows with WSL2

### Development Environment Setup

#### 1. Fork and Clone Repository

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/rmf-monitor-simulator.git
cd rmf-monitor-simulator

# Add upstream remote
git remote add upstream https://github.com/original-org/rmf-monitor-simulator.git
```

#### 2. Install Poetry

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Or using pip
pip install poetry
```

#### 3. Set Up Python Environment

```bash
# Install dependencies
poetry install

# Install development dependencies
poetry install --group dev

# Activate virtual environment
poetry shell
```

#### 4. Install Pre-commit Hooks

```bash
# Install pre-commit hooks for code quality
poetry run pre-commit install

# Run pre-commit on all files (optional)
poetry run pre-commit run --all-files
```

#### 5. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your local settings
nano .env
```

Example `.env` file:
```bash
# Application Settings
LOG_LEVEL=DEBUG
PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc_dir

# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=rmf_monitoring_dev
MYSQL_USER=rmf_dev_user
MYSQL_PASSWORD=rmf_dev_password
MYSQL_ROOT_PASSWORD=root_dev_password

# MongoDB Configuration
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DATABASE=rmf_monitoring_dev
MONGO_USERNAME=rmf_dev_user
MONGO_PASSWORD=rmf_dev_password
MONGO_AUTH_SOURCE=rmf_monitoring_dev

# S3/MinIO Configuration
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=rmf_dev_user
S3_SECRET_KEY=rmf_dev_password123
S3_BUCKET_NAME=rmf-metrics-dev
S3_REGION=us-east-1
S3_USE_SSL=false
```

#### 6. Start Development Infrastructure

```bash
# Start all required services
docker-compose -f docker-compose.dev.yml up -d

# Verify services are running
docker-compose -f docker-compose.dev.yml ps
```

#### 7. Initialize Databases

```bash
# Create database schemas and initial data
poetry run python scripts/init_databases.py

# Verify database connectivity
poetry run python -c "
from storage.mysql.service import DatabaseService
from storage.mongodb.service import MongoDBService
from storage.S3.s3 import S3StorageService

print('MySQL:', DatabaseService().get_connection_status())
print('MongoDB:', MongoDBService().get_connection_status())
print('S3:', S3StorageService().get_connection_status())
"
```

#### 8. Run the Application

```bash
# Start the FastAPI application in development mode
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the development script
poetry run python scripts/run_dev.py
```

#### 9. Verify Setup

Open your browser and navigate to:
- **Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Metrics**: http://localhost:8000/metrics
- **Health Check**: http://localhost:8000/health

## 🧪 Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_simulator.py

# Run tests with verbose output
poetry run pytest -v

# Run tests and watch for changes
poetry run pytest-watch
```

### Test Categories

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test database and storage integrations
3. **API Tests**: Test FastAPI endpoints
4. **Performance Tests**: Test metric generation performance

### Writing Tests

Create test files in the `tests/` directory:

```python
# tests/test_new_feature.py
import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_new_endpoint():
    response = client.get("/new-endpoint")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

## 🎯 Code Style and Standards

### Python Code Style

We use the following tools for code quality:

1. **Black**: Code formatting
2. **isort**: Import sorting
3. **flake8**: Linting
4. **mypy**: Type checking
5. **bandit**: Security linting

### Running Code Quality Checks

```bash
# Format code
poetry run black .
poetry run isort .

# Lint code
poetry run flake8 .
poetry run mypy .

# Security check
poetry run bandit -r app/

# Run all checks
poetry run pre-commit run --all-files
```

### Code Style Guidelines

1. **PEP 8 Compliance**: Follow Python PEP 8 style guide
2. **Type Hints**: Use type hints for all function parameters and return values
3. **Docstrings**: Use Google-style docstrings for all functions and classes
4. **Error Handling**: Implement proper exception handling with logging
5. **Testing**: Write tests for all new functionality

Example function:
```python
def calculate_cpu_utilization(
    base_utilization: float, 
    time_factor: float,
    workload_type: str
) -> float:
    """Calculate CPU utilization based on workload patterns.
    
    Args:
        base_utilization: Base CPU utilization percentage
        time_factor: Time-based multiplication factor
        workload_type: Type of workload (online, batch, mixed)
        
    Returns:
        Calculated CPU utilization percentage
        
    Raises:
        ValueError: If base_utilization is negative or > 100
    """
    if base_utilization < 0 or base_utilization > 100:
        raise ValueError("Base utilization must be between 0 and 100")
    
    # Calculate utilization logic here
    utilization = min(95.0, base_utilization * time_factor)
    
    logger.debug(f"Calculated CPU utilization: {utilization}%")
    return utilization
```

## 📁 Project Structure

```
rmf-monitor-simulator/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── models/                 # Data models
│   ├── simulator/              # Simulation logic
│   └── api/                    # API endpoints
├── storage/
│   ├── mysql/                  # MySQL integration
│   ├── mongodb/                # MongoDB integration
│   └── S3/                     # S3/MinIO integration
├── utils/
│   ├── logger.py               # Logging configuration
│   ├── config.py               # Configuration management
│   └── helpers.py              # Utility functions
├── tests/
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── fixtures/               # Test fixtures
├── docs/                       # Documentation
├── k8s/                        # Kubernetes manifests
├── grafana/                    # Grafana dashboards
├── prometheus/                 # Prometheus configuration
├── scripts/                    # Development scripts
├── docker-compose.yml          # Production compose file
├── docker-compose.dev.yml      # Development compose file
├── Dockerfile                  # Container image
├── pyproject.toml              # Poetry configuration
└── README.md                   # Project documentation
```

## 🚀 Development Workflow

### 1. Create Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b bugfix/issue-description
```

### 2. Make Changes

1. **Write Code**: Implement your feature or fix
2. **Add Tests**: Write comprehensive tests
3. **Update Documentation**: Update relevant documentation
4. **Run Tests**: Ensure all tests pass

### 3. Commit Changes

```bash
# Add changes
git add .

# Commit with conventional commit format
git commit -m "feat: add new CPU metric calculation

- Implement specialty engine utilization logic
- Add comprehensive test coverage
- Update documentation with new metrics"
```

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes
- **refactor**: Code refactoring
- **test**: Test additions/modifications
- **chore**: Maintenance tasks

### 4. Push and Create Pull Request

```bash
# Push feature branch
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## 🔧 Advanced Development

### Custom Storage Backend

To add a new storage backend:

1. Create a new module in `storage/your_backend/`
2. Implement the storage interface
3. Add configuration options
4. Update the simulator to use the new backend
5. Add comprehensive tests

Example structure:
```python
# storage/your_backend/service.py
from abc import ABC, abstractmethod
from typing import Dict, List
from datetime import datetime

class StorageBackend(ABC):
    @abstractmethod
    def store_metric(self, metric_data: Dict) -> bool:
        pass
    
    @abstractmethod
    def get_connection_status(self) -> Dict:
        pass

class YourStorageService(StorageBackend):
    def __init__(self, config):
        self.config = config
        self.initialize_connection()
    
    def store_metric(self, metric_data: Dict) -> bool:
        # Implementation here
        pass
```

### Adding New Metrics

1. **Define Prometheus Metric**: Add to `metrics/definitions.py`
2. **Implement Simulation Logic**: Add to `simulator/mainframe.py`
3. **Add Storage Methods**: Update all storage backends
4. **Create Tests**: Add comprehensive test coverage
5. **Update Documentation**: Add metric description

### Performance Optimization

1. **Profiling**: Use `cProfile` for performance analysis
2. **Async Operations**: Use asyncio for I/O operations
3. **Batch Processing**: Implement batch writes for storage
4. **Caching**: Add Redis caching for frequently accessed data

## 🐳 Docker Development

### Development Container

```bash
# Build development image
docker build -f Dockerfile.dev -t rmf-simulator:dev .

# Run development container
docker run -it --rm \
  -v $(pwd):/app \
  -p 8000:8000 \
  rmf-simulator:dev bash
```

### Multi-stage Builds

The production Dockerfile uses multi-stage builds:

```dockerfile
# Build stage
FROM python:3.11-slim as builder
# ... build dependencies

# Production stage
FROM python:3.11-slim as production
# ... production setup
```

## 📊 Monitoring Development

### Local Monitoring Stack

```bash
# Start monitoring services
docker-compose -f docker-compose.dev.yml up -d prometheus grafana

# Import dashboards
curl -X POST \
  http://admin:admin@localhost:3000/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @grafana/dashboards/development.json
```

### Custom Metrics for Development

Add development-specific metrics:

```python
from prometheus_client import Counter, Histogram

# Development metrics
DEV_REQUESTS = Counter('dev_requests_total', 'Development requests')
DEV_PROCESSING_TIME = Histogram('dev_processing_seconds', 'Processing time')
```

## 🔍 Debugging

### Debugging FastAPI Application

```bash
# Run with debugger
poetry run python -m debugpy --listen 5678 --wait-for-client -m uvicorn app.main:app --reload

# Or use VSCode launch configuration
```

### Database Debugging

```bash
# Connect to MySQL
docker-compose exec mysql mysql -u root -p

# Connect to MongoDB
docker-compose exec mongodb mongosh

# View MinIO files
docker-compose exec minio mc ls local/rmf-metrics/
```

### Log Analysis

```bash
# View application logs
docker-compose logs -f rmf-simulator

# View all service logs
docker-compose logs -f

# Filter logs by level
docker-compose logs rmf-simulator | grep ERROR
```

## 📝 Documentation

### API Documentation

Update OpenAPI documentation:

```python
@app.get("/new-endpoint", 
         summary="New endpoint description",
         description="Detailed description of the endpoint",
         response_model=ResponseModel)
async def new_endpoint():
    """
    New endpoint implementation
    
    Returns:
        ResponseModel: Description of return value
    """
    pass
```

### Adding Documentation

1. **API Changes**: Update docstrings and OpenAPI specs
2. **Configuration**: Update configuration documentation
3. **Deployment**: Update deployment guides
4. **Tutorials**: Add step-by-step tutorials

## 🚀 Release Process

### Version Management

We use semantic versioning (SemVer):

```bash
# Update version in pyproject.toml
poetry version patch  # 1.0.0 -> 1.0.1
poetry version minor  # 1.0.0 -> 1.1.0
poetry version major  # 1.0.0 -> 2.0.0
```

### Creating Releases

1. **Update Version**: Update version in `pyproject.toml`
2. **Update Changelog**: Add release notes to `CHANGELOG.md`
3. **Create Release Branch**: `git checkout -b release/v1.0.0`
4. **Test Release**: Run full test suite
5. **Create Tag**: `git tag v1.0.0`
6. **Push Release**: `git push origin v1.0.0`

## 🤝 Pull Request Guidelines

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass and coverage is maintained
- [ ] Documentation is updated
- [ ] Commits follow conventional format
- [ ] No merge conflicts with main branch

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added for new functionality
```

## 🆘 Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Development Chat**: Join our development Slack/Discord
- **Code Review**: Request review from maintainers

## 📋 Maintainer Guidelines

### Code Review Process

1. **Automated Checks**: Ensure CI passes
2. **Code Quality**: Review code style and structure
3. **Test Coverage**: Verify adequate test coverage
4. **Documentation**: Check documentation updates
5. **Performance**: Consider performance implications

### Merge Criteria

- All CI checks pass
- At least one maintainer approval
- No unresolved conversations
- Documentation updated
- Tests added for new features

Thank you for contributing to the RMF Monitor III Data Simulator! 🎉