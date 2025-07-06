import random

class VolumeSimulator:
    def __init__(self, num_volumes=3):
        self.num_volumes = num_volumes
        self.volumes = []
        for i in range(1, num_volumes+1):
            name = f"VOL{i:02d}"
            # Capacity in MB (100GB to 500GB)
            capacity = random.randint(100*1024, 500*1024)
            self.volumes.append({
                "name": name,
                "capacity_mb": capacity,
                "used_mb": 0,
                "free_mb": capacity,
                "percent_used": 0.0,
                "io_rate_ops": 0
            })

    def update(self):
        for vol in self.volumes:
            used = random.randint(0, int(0.9 * vol["capacity_mb"]))
            vol["used_mb"] = used
            vol["free_mb"] = vol["capacity_mb"] - used
            vol["percent_used"] = round(used / vol["capacity_mb"] * 100, 1)
            vol["io_rate_ops"] = random.randint(0, 500)

    def get_metrics(self):
        return {"volumes": self.volumes}
