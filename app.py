import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.logger import logger
from routes import health, metrics
from dotenv import load_dotenv

load_dotenv()

# Check if storage services are enabled
storage_enabled = (
    os.getenv("ENABLE_MYSQL", "false").lower() == "true" or 
    os.getenv("ENABLE_MONGO", "false").lower() == "true" or 
    os.getenv("ENABLE_S3", "false").lower() == "true"
)

# Import modules (now unified)
from metrices.updater import start_updater
from routes import system

# Set app configuration based on storage enabled status
if storage_enabled:
    app_title = "RMF Monitor III Data Simulator"
    app_description = "Production-ready z/OS metrics simulator with realistic workload patterns"
    logger.info("Starting in full mode with storage services")
else:
    # Force disable all storage services for prometheus-only mode
    os.environ["ENABLE_MYSQL"] = "false"
    os.environ["ENABLE_MONGO"] = "false" 
    os.environ["ENABLE_S3"] = "false"
    
    app_title = "RMF Monitor III Data Simulator (Prometheus Only)"
    app_description = "Prometheus-only z/OS metrics simulator - no storage dependencies"
    logger.info("Starting in prometheus-only mode - storage services disabled")

app = FastAPI(
    title=app_title,
    description=app_description,
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    start_updater()
    if storage_enabled:
        logger.info("Simulator startup complete with storage services.")
    else:
        logger.info("Simulator-only mode startup complete - no storage services initialized")

# Include core routers
app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(system.router)

# Conditionally include storage router only if storage services are enabled
if storage_enabled:
    try:
        from routes import storage
        app.include_router(storage.router)
        logger.info("Storage routes enabled")
    except Exception as e:
        logger.warning(f"Failed to load storage routes: {e}")
else:
    logger.info("Storage routes disabled - all storage services are disabled")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
