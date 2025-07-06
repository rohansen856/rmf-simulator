import random

class IOSimulator:
    def __init__(self):
        self.io_rate = 0  # I/O operations per second
        self.io_utilization = 0.0  # percent

    def update(self):
        # Simulate I/O rate (IOPS) and utilization percentage
        self.io_rate = random.randint(100, 1000)
        self.io_utilization = round(random.uniform(0, 100), 1)

    def get_metrics(self):
        return {
            "io_rate_ops": self.io_rate,
            "io_subsystem_utilization_percent": self.io_utilization
        }
