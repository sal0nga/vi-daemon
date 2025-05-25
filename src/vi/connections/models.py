from datetime import datetime

class Connection:
    def __init__(self, pid, process_name, user, local_ip, local_port, remote_ip, remote_port, status,
                 cpu_percent=None, memory_rss=None, timestamp=None):
        self.pid = int(pid)
        self.process_name = process_name
        self.user = user
        self.local_ip = local_ip
        self.local_port = int(local_port)
        self.remote_ip = remote_ip
        self.remote_port = int(remote_port)
        self.status = status
        self.cpu_percent = cpu_percent
        self.memory_rss = memory_rss
        self.timestamp = timestamp or datetime.now().astimezone()

    def __repr__(self):
        return (f"<Connection {self.process_name} (PID {self.pid}) "
                f"{self.local_ip}:{self.local_port} -> "
                f"{self.remote_ip}:{self.remote_port} [{self.status}]>")