import random

class CLPRSimulator:
    def __init__(self, num_clpr=1):
        self.num_clpr = num_clpr
        self.clprs = []
        for i in range(1, num_clpr+1):
            clpr_number = i-1
            clpr_name = f"CLPR{clpr_number}"
            self.clprs.append({
                "clpr_number": clpr_number,
                "clpr_name": clpr_name,
                "utilization_pct": 0.0,
                "write_pending_pct": 0.0,
                "cfw_pending_pct": 0.0,
                "side_file_pct": 0.0,
                "random_reads": 0,
                "random_read_hits": 0,
                "random_writes": 0,
                "random_write_hits": 0,
                "seq_reads": 0,
                "seq_read_hits": 0,
                "seq_writes": 0,
                "seq_write_hits": 0,
                "cfw_read_hits": 0,
                "cfw_writes": 0,
                "cfw_reads": 0,
                "cfw_write_hits": 0,
                "seq_tracks_to_cache": 0,
                "random_tracks_to_cache": 0,
                "tracks_cache_to_dr": 0,
                "data_to_cache_mb": 0,
                "data_to_dr_mb": 0
            })

    def update(self):
        for clpr in self.clprs:
            clpr["utilization_pct"] = round(random.uniform(0, 100), 1)
            clpr["write_pending_pct"] = round(random.uniform(0, 100), 1)
            clpr["cfw_pending_pct"] = round(random.uniform(0, 100), 1)
            clpr["side_file_pct"] = round(random.uniform(0, 100), 1)
            random_reads = random.randint(0, 10000)
            clpr["random_reads"] = random_reads
            clpr["random_read_hits"] = random.randint(0, random_reads)
            random_writes = random.randint(0, 10000)
            clpr["random_writes"] = random_writes
            clpr["random_write_hits"] = random.randint(0, random_writes)
            seq_reads = random.randint(0, 10000)
            clpr["seq_reads"] = seq_reads
            clpr["seq_read_hits"] = random.randint(0, seq_reads)
            seq_writes = random.randint(0, 10000)
            clpr["seq_writes"] = seq_writes
            clpr["seq_write_hits"] = random.randint(0, seq_writes)
            cfw_reads = random.randint(0, 1000)
            clpr["cfw_reads"] = cfw_reads
            clpr["cfw_read_hits"] = random.randint(0, cfw_reads)
            cfw_writes = random.randint(0, 1000)
            clpr["cfw_writes"] = cfw_writes
            clpr["cfw_write_hits"] = random.randint(0, cfw_writes)
            clpr["seq_tracks_to_cache"] = random.randint(0, 1000)
            clpr["random_tracks_to_cache"] = random.randint(0, 1000)
            clpr["tracks_cache_to_dr"] = random.randint(0, 1000)
            clpr["data_to_cache_mb"] = random.randint(0, 50000)
            clpr["data_to_dr_mb"] = random.randint(0, 50000)

    def get_metrics(self):
        return {"clpr": self.clprs}
