import random

class PortSimulator:
    def __init__(self, num_ports=2):
        self.num_ports = num_ports
        self.ports = []
        for i in range(1, num_ports+1):
            port_id = i
            adapter_id = random.randint(0, 100)
            wwn = ''.join(random.choices('0123456789ABCDEF', k=16))
            link_type = random.choice(['ECKD', 'FICON', 'ESC'])
            link_address = ''.join(random.choices('0123456789ABCDEF', k=8))
            self.ports.append({
                "port_id": port_id,
                "adapter_id": adapter_id,
                "wwn": wwn,
                "link_type": link_type,
                "link_address": link_address,
                "cmd_read_ssch_count": 0,
                "cmd_write_ssch_count": 0,
                "xport_read_ssch_count": 0,
                "xport_write_ssch_count": 0,
                "cmd_read_transfer_mb": 0,
                "cmd_write_transfer_mb": 0,
                "xport_read_transfer_mb": 0
            })

    def update(self):
        for port in self.ports:
            port["cmd_read_ssch_count"] = random.randint(0, 10000)
            port["cmd_write_ssch_count"] = random.randint(0, 10000)
            port["xport_read_ssch_count"] = random.randint(0, 5000)
            port["xport_write_ssch_count"] = random.randint(0, 5000)
            port["cmd_read_transfer_mb"] = random.randint(0, 1000)
            port["cmd_write_transfer_mb"] = random.randint(0, 1000)
            port["xport_read_transfer_mb"] = random.randint(0, 500)

    def get_metrics(self):
        return {"ports": self.ports}
