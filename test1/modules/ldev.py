import random

class LDEVSimulator:
    def __init__(self, num_ldev=2):
        self.num_ldev = num_ldev
        self.ldevs = []
        for i in range(1, num_ldev+1):
            ldev_name = f"LDEV{i}"
            self.ldevs.append({
                "ldev_name": ldev_name,
                "random_reads": 0,
                "random_read_hits": 0,
                "random_writes": 0,
                "random_write_hits": 0,
                "seq_reads": 0,
                "seq_read_hits": 0,
                "seq_writes": 0,
                "seq_write_hits": 0
            })

    def update(self):
        for ldev in self.ldevs:
            rr = random.randint(0, 5000)
            ldev["random_reads"] = rr
            ldev["random_read_hits"] = random.randint(0, rr)
            rw = random.randint(0, 5000)
            ldev["random_writes"] = rw
            ldev["random_write_hits"] = random.randint(0, rw)
            sr = random.randint(0, 5000)
            ldev["seq_reads"] = sr
            ldev["seq_read_hits"] = random.randint(0, sr)
            sw = random.randint(0, 5000)
            ldev["seq_writes"] = sw
            ldev["seq_write_hits"] = random.randint(0, sw)

    def get_metrics(self):
        return {"ldevs": self.ldevs}
