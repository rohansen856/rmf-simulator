# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RMF Monitor III Data Simulator is a production-ready z/OS mainframe metrics simulator that generates realistic IBM RMF (Resource Measurement Facility) Monitor III data with authentic workload patterns, comprehensive storage backends, and modern monitoring integration.

## Development Commands

### Running the Application

**Unified Entry Point**: The application now uses a single entry point (`app.py`) that automatically detects the configuration and runs in the appropriate mode.

```bash
# Prometheus-only mode (no storage services)
# Set all storage services to false in .env or environment:
# ENABLE_MYSQL=false
# ENABLE_MONGO=false
# ENABLE_S3=false
python app.py

# Full mode with storage services
# Enable desired storage services in .env:
# ENABLE_MYSQL=true
# ENABLE_MONGO=true  
# ENABLE_S3=true
python app.py

# Using the flexible run script
python run.py simulator-only    # Prometheus metrics only
python run.py full              # All services enabled
python run.py custom            # Use .env configuration (default)
```

**Alternative Methods**
```bash
# Using Poetry (recommended)
poetry install
poetry run uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Using requirements.txt
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Code Quality
```bash
# Format code
poetry run black .

# Sort imports
poetry run isort .

# Lint code
poetry run flake8

# Run all quality checks
poetry run black . && poetry run isort . && poetry run flake8
```

### Testing
```bash
# Run tests
poetry run pytest

# Run tests with async support
poetry run pytest -v --asyncio-mode=auto

# Run specific test file
poetry run pytest tests/test_specific.py
```

### Docker Development
```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs rmf-simulator

# Stop services
docker-compose down
```

## Architecture Overview

### Core Components

1. **MainframeSimulator** (`metrices/simulator.py`): Central orchestrator that coordinates metric generation across all subsystems using a modular simulator factory pattern. Automatically adapts to prometheus-only mode when no storage services are enabled.

2. **Storage Manager** (`storage/storage_manager.py`): Multi-backend storage abstraction that simultaneously writes to MySQL, MongoDB, and S3 with batching optimizations for S3. Gracefully handles cases where no storage backends are available.

3. **Simulator Factory** (`metrices/simulators/factory.py`): Factory pattern implementation that creates specific simulators for different metric types (CPU, memory, storage, network, etc.).

4. **FastAPI Application** (`app.py`): Unified web application that automatically configures itself based on environment variables, providing REST endpoints, Prometheus metrics, and health checks. Conditionally loads storage routes only when storage services are enabled.

### Key Patterns

- **Modular Simulators**: Each metric type (CPU, memory, LDEV, etc.) has its own simulator class following a common interface
- **Multi-Storage Architecture**: Simultaneous writes to MySQL (relational), MongoDB (document), and S3 (object storage)
- **Time-based Workload Simulation**: Realistic peak hours, workload types (online/batch/mixed), and cyclical patterns
- **LPAR-based Organization**: Metrics organized by Logical Partition (LPAR) configurations representing different mainframe workloads

### Directory Structure

- `metrices/`: Core simulation logic and metric generators
  - `simulators/`: Individual simulator implementations (CPU, memory, storage, etc.)
  - `definitions.py`: Prometheus metric definitions
  - `simulator.py`: Main simulator orchestrator
  - `updater.py`: Background task scheduler
- `storage/`: Multi-backend storage implementations
  - `mysql/`: Relational database storage with optimized schemas
  - `mongodb/`: NoSQL document storage for flexible metrics
  - `S3/`: Object storage for long-term archival
  - `storage_manager.py`: Unified storage interface
- `routes/`: FastAPI route handlers for different API endpoints
- `models/`: Data models and enums (LPAR configs, metric types)
- `utils/`: Shared utilities (logging, configuration)

### Configuration

**LPAR Configuration**: Modify `utils/confiig.py` to customize mainframe environment:
```python
LPAR_CONFIGS = [
    LPARConfig("PROD01", 16, 64, "online", [8, 9, 10, 14, 15, 16]),
    # name, cpu_capacity, memory_gb, workload_type, peak_hours
]
```

**Environment Variables**: See README.md for complete list of database and S3 configuration options.

**Service Configuration**: The application automatically detects the configuration mode:
- **Prometheus-only mode**: When all storage services are disabled (`ENABLE_MYSQL=false`, `ENABLE_MONGO=false`, `ENABLE_S3=false`), the application runs in prometheus-only mode with no storage dependencies
- **Full mode**: When any storage service is enabled, the application runs with full functionality including storage routes
- `ENABLED_SIMULATORS`: Comma-separated list of simulators to enable (applies to both modes)

## Development Guidelines

### Code Conventions
- Follow existing patterns in simulator implementations
- Use the factory pattern for new simulator types
- Maintain consistent error handling and logging throughout
- All new simulators should extend the base simulator interface
- Database operations should go through the storage manager, not directly to services

### Adding New Metrics
1. Create simulator class in `metrices/simulators/`
2. Register in `metrices/simulators/factory.py`
3. Add Prometheus metric definitions in `metrices/definitions.py`
4. Update storage manager methods for new metric types
5. Add database schema changes to MySQL/MongoDB services

### Testing Strategy
- Use pytest with async support for API testing
- Mock external dependencies (databases, S3)
- Test individual simulators in isolation
- Integration tests should use docker-compose test environment

### Performance Considerations
- Metrics update every 15 seconds across all LPARs
- S3 operations are batched (50 items or 60 seconds)
- Database connections are pooled and reused
- Avoid blocking operations in the main simulation loop

## Troubleshooting

### Common Issues
- **Port conflicts**: Default ports are 8000 (app), 3306 (MySQL), 27017 (MongoDB), 9000/9001 (MinIO)
- **Database connectivity**: Check docker-compose services are running and environment variables are set
- **Memory usage**: Full stack requires 8GB+ RAM for optimal performance
- **Metric generation**: Check logs for simulator initialization errors

### Debug Commands
```bash
# Check service health
curl http://localhost:8000/health

# View Prometheus metrics
curl http://localhost:8000/metrics

# Check system info
curl http://localhost:8000/system-info

# Test database connectivity
docker-compose exec rmf-simulator python -c "from storage.mysql.service import DatabaseService; print(DatabaseService().get_connection_status())"
```