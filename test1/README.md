# z/OS RMF Monitor III Metrics Simulator

This project provides a Python-based simulator for IBM z/OS RMF Monitor III metrics, packaged as a container. The simulator generates fake data for various system resources (CPU, memory, I/O, volumes, MPBs, CLPRs, LDEVs) and exposes them via REST APIs.

## Project Structure

- `app.py`: Main FastAPI application. Defines endpoints and starts a 30-second update loop.
- `modules/`: Contains simulator modules for each resource type (`cpu.py`, `memory.py`, etc.).
- `requirements.txt`: Python dependencies.
- `Dockerfile`: Docker build instructions.
- `docker-compose.yml`: (Optional) Docker Compose setup.

## Running the Simulator

1. **Using Docker**:
   - Build the image: `docker build -t rmf-sim .`
   - Run the container: `docker run -d -p 8000:8000 rmf-sim`
   - The API will be available at `http://localhost:8000/api/v1/metrics` and `http://localhost:8000/api/v1/volumes`.

2. **Using Docker Compose**:
   - Run: `docker-compose up --build -d`
   - Access the endpoints as above.

## API Usage

- `GET /api/v1/metrics`: Returns all simulated metrics in JSON format (CPU, memory, I/O, volumes, ports, MPB, CLPR, LDEV).
- `GET /api/v1/volumes`: Returns only the volume metrics (array of volumes with usage stats).

_Example JSON output for `/api/v1/metrics`_:
```json
{
  "cpu": { "cpu_usage_percent": 57.3, "cpu_wait_percent": 12.1 },
  "memory": { "total_memory_mb": 262144, "used_memory_mb": 158786, "free_memory_mb": 103358, "usage_percent": 60.6 },
  "io_subsystem": { "io_rate_ops": 724, "io_subsystem_utilization_percent": 42.5 },
  "volumes": [
    { "name": "VOL01", "capacity_mb": 204800, "used_mb": 102400, "free_mb": 102400, "percent_used": 50.0, "io_rate_ops": 120 },
    ...
  ],
  ...
}
```

## Extending the Simulator
To add new metrics:

- Create a module in `modules/` with an `update()` method that modifies its state and `get_metrics()` to return a dict.
- Register it in `app.py` by instantiating the class, calling `update()` in `periodic_update()`, and including it in the `/metrics` response.

## Grafana Integration
You can point Grafana to this API using the JSON API plugin. For example:

- Add a JSON API data source with URL `http://<host>:8000/api/v1/`.
- Create panels querying `/metrics` or `/volumes` as needed.
- Use Grafana variables and queries to extract fields (e.g. `cpu.cpu_usage_percent` or `volumes[].percent_used`).
- The IBM RMF Grafana plugin docs provide examples of similar queries for real RMF data; you can adapt them to point to this simulator.

```sh
# Install JSON API plugin in Grafana (if not already):
grafana-cli plugins install marcusolsson-json-datasource

# Example Grafana query (JSON path):
# For CPU usage: $.cpu.cpu_usage_percent
# For volume freespace: $.volumes[*].percent_used
```