import random

class CPUSimulator:
    def __init__(self):
        # Initialize baseline CPU usage and wait time
        self.cpu_usage = 0.0
        self.cpu_wait = 0.0

    def update(self):
        # Simulate CPU utilization and wait percentage (0-100%)
        self.cpu_usage = round(random.uniform(0, 100), 1)
        self.cpu_wait = round(random.uniform(0, 50), 1)

    def get_metrics(self):
        return {
            "cpu_usage_percent": self.cpu_usage,
            "cpu_wait_percent": self.cpu_wait
        }
