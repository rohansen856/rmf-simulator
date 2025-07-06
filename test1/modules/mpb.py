import random

class MPBSimulator:
    def __init__(self, num_mp=2):
        self.num_mp = num_mp
        self.mpbs = []
        for i in range(1, num_mp+1):
            mp_id = i
            mp_name = f"MP{i-1}"
            self.mpbs.append({
                "mp_id": mp_id,
                "mp_name": mp_name,
                "utilization_pct": 0.0,
                "ot_port_util_pct": 0.0,
                "oi_port_util_pct": 0.0,
                "oe_port_util_pct": 0.0
            })

    def update(self):
        for mp in self.mpbs:
            mp["utilization_pct"] = round(random.uniform(0, 100), 1)
            mp["ot_port_util_pct"] = round(random.uniform(0, 100), 1)
            mp["oi_port_util_pct"] = round(random.uniform(0, 100), 1)
            mp["oe_port_util_pct"] = round(random.uniform(0, 100), 1)

    def get_metrics(self):
        return {"mpb": self.mpbs}
