import asyncio
from metrices.simulator import simulator
from utils.logger import logger

def start_updater():
    """Start the metrics updater (works with both full and prometheus-only modes)"""
    async def metrics_updater():
        while True:
            try:
                await simulator.update_all_metrics()
                mode = simulator.get_simulator_status().get('mode', 'full')
                if mode == 'prometheus_only':
                    logger.info("Metrics updated successfully (Prometheus only)")
                else:
                    logger.info("Metrics updated successfully")
            except Exception as e:
                logger.error(f"Error updating metrics: {e}")
            await asyncio.sleep(15)

    asyncio.create_task(metrics_updater())
