from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from metrices.updater import start_updater
from utils.logger import logger
from routes import health, metrics, system, storage
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="RMF Monitor III Data Simulator",
    description="Production-ready z/OS metrics simulator with realistic workload patterns",
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
    logger.info("Simulator startup complete.")

# Include routers
app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(system.router)
app.include_router(storage.router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
