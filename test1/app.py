from fastapi import FastAPI
from modules.cpu import CPUSimulator
from modules.memory import MemorySimulator
from modules.io_subsystem import IOSimulator
from modules.volumes import VolumeSimulator
from modules.ports import PortSimulator
from modules.mpb import MPBSimulator
from modules.clpr import CLPRSimulator
from modules.ldev import LDEVSimulator
from contextlib import asynccontextmanager
import asyncio

app = FastAPI(
    title="z/OS RMF Monitor III Metrics Simulator",
    description="A simulator for IBM z/OS RMF Monitor III metrics",
    version="1.0"
)

# Initialize simulator instances
cpu_sim = CPUSimulator()
mem_sim = MemorySimulator()
io_sim = IOSimulator()
volume_sim = VolumeSimulator()
port_sim = PortSimulator()
mpb_sim = MPBSimulator()
clpr_sim = CLPRSimulator()
ldev_sim = LDEVSimulator()

async def periodic_update():
    while True:
        # Update all simulators
        cpu_sim.update()
        mem_sim.update()
        io_sim.update()
        volume_sim.update()
        port_sim.update()
        mpb_sim.update()
        clpr_sim.update()
        ldev_sim.update()
        await asyncio.sleep(30)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background task to update metrics every 30 seconds
    task = asyncio.create_task(periodic_update())
    yield
    task.cancel()
    await task

@app.get("/api/v1/metrics")
async def get_metrics():
    """
    Get all simulated RMF Monitor III metrics.
    """
    return {
        "cpu": cpu_sim.get_metrics(),
        "memory": mem_sim.get_metrics(),
        "io_subsystem": io_sim.get_metrics(),
        "volumes": volume_sim.get_metrics()["volumes"],
        "ports": port_sim.get_metrics()["ports"],
        "mpb": mpb_sim.get_metrics()["mpb"],
        "clpr": clpr_sim.get_metrics()["clpr"],
        "ldev": ldev_sim.get_metrics()["ldevs"]
    }

@app.get("/")
async def get_root():
    return "Server running"

@app.get("/api/v1/volumes")
async def get_volumes():
    """
    Get only volume metrics.
    """
    return {"volumes": volume_sim.get_metrics()["volumes"]}

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )