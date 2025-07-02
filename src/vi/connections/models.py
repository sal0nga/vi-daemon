from datetime import datetime

class Connection:
    def __init__(self, pid, process_name, user, local_ip, local_port, remote_ip, remote_port, status,
                 cpu_percent=None, memory_rss=None, timestamp=None, tag=None,
                 connection_count=None, duration_seconds=None, is_remote_ipv6=None, anomaly_score=None):
        self.pid = int(pid)
        self.process_name = process_name
        self.user = user
        self.local_ip = local_ip
        self.local_port = int(local_port)
        self.remote_ip = remote_ip
        self.remote_port = int(remote_port)
        self.status = status
        self.cpu_percent = cpu_percent if cpu_percent is not None else 0.0
        self.memory_rss = memory_rss if memory_rss is not None else 0
        self.timestamp = timestamp or datetime.now().astimezone()
        self.tag = tag if tag is not None else 'untagged'
        self.connection_count = connection_count if connection_count is not None else 0
        self.duration_seconds = duration_seconds if duration_seconds is not None else 0.0
        self.is_remote_ipv6 = is_remote_ipv6 if is_remote_ipv6 is not None else False
        self.anomaly_score = anomaly_score if anomaly_score is not None else 0.0

    def __repr__(self):
        return (f"<Connection {self.process_name} (PID {self.pid}) "
                f"{self.local_ip}:{self.local_port} -> "
                f"{self.remote_ip}:{self.remote_port} [{self.status}] | Anomaly Score: {self.anomaly_score}>")