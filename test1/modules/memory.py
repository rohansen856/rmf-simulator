import random

class MemorySimulator:
    def __init__(self):
        # Total memory in MB (e.g., 256GB)
        self.total_memory_mb = 256 * 1024
        self.used_memory_mb = 0

    def update(self):
        # Simulate used memory between 20% and 90% of total
        self.used_memory_mb = random.randint(
            int(0.2 * self.total_memory_mb),
            int(0.9 * self.total_memory_mb)
        )

    def get_metrics(self):
        free_mb = self.total_memory_mb - self.used_memory_mb
        used_pct = round(self.used_memory_mb / self.total_memory_mb * 100, 1)
        return {
            "total_memory_mb": self.total_memory_mb,
            "used_memory_mb": self.used_memory_mb,
            "free_memory_mb": free_mb,
            "usage_percent": used_pct
        }
