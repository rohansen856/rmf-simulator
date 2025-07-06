import asyncio
from metrices.simulator import simulator
from utils.logger import logger

def start_updater():
    async def metrics_updater():
        while True:
            try:
                await simulator.update_all_metrics()
                logger.info("Metrics updated successfully")
            except Exception as e:
                logger.error(f"Error updating metrics: {e}")
            await asyncio.sleep(15)

    asyncio.create_task(metrics_updater())
