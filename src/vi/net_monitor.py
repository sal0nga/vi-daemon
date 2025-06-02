# Discovers all current TCP/UDP connections w/ lsof
import subprocess
import re
import logging
import time
from connections import Connection
import psutil

# Store previous cpu times for each pid
_previous_cpu_times: dict[int, tuple[float, float]] = {}

# Helper to calculate cpu percent for a process
def calculate_cpu_percent(pid: int, current_time: float, current_cpu_time: float) -> float:
    if pid not in _previous_cpu_times:
        _previous_cpu_times[pid] = (current_cpu_time, current_time)
        return 0.0

    prev_cpu_time, prev_time = _previous_cpu_times[pid]
    delta_cpu = current_cpu_time - prev_cpu_time
    delta_time = current_time - prev_time

    _previous_cpu_times[pid] = (current_cpu_time, current_time)

    if delta_time <= 0:
        return 0.0

    return (delta_cpu / delta_time) * 100

# Extracts local/remote IPs & ports, PID, process name & user
def get_active_connections():
    connections = []

    try:
        result = subprocess.run(
            ['lsof', '-i', '-n', '-P'],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )

        lines = result.stdout.strip().split('\n')
        for line in lines:
            if 'ESTABLISHED' not in line:
                continue

            parts = re.split(r'\s+', line)
            if len(parts) < 9:
                continue

            name, pid, user, fd, type_, device, size_off, node, name_field = parts[:9]

            if '->' not in name_field:
                continue

            pid = int(pid)
            try:
                proc = psutil.Process(pid)
                cpu_times = proc.cpu_times()
                total_cpu_time = cpu_times.user + cpu_times.system
                now = time.time()
                cpu = calculate_cpu_percent(pid, now, total_cpu_time)
                mem = proc.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                cpu = 0.0
                mem = 0

            local, remote = name_field.split('->')
            l_ip, l_port = local.rsplit(':', 1)
            r_ip, r_port = remote.rsplit(':', 1)

            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

            is_ipv6 = 1 if ':' in r_ip else 0
            conn = Connection(
                pid=pid,
                process_name=name,
                user=user,
                local_ip=l_ip,
                local_port=int(l_port),
                remote_ip=r_ip,
                remote_port=int(r_port),
                status='ESTABLISHED',
                cpu_percent=cpu,
                memory_rss=mem,
                timestamp=timestamp,
                tag='untagged',
                connection_count=None,
                duration_seconds=None,
                is_remote_ipv6=is_ipv6
            )

            logging.info(f'     {conn}')
            connections.append(conn)

    except Exception as e:
        logging.warning(f"[WARN] Failed to read connections via lsof: {e}")

    # Compute connection_count for each Connection object
    pid_counts: dict[int, int] = {}
    for c in connections:
        pid_counts[c.pid] = pid_counts.get(c.pid, 0) + 1
    for c in connections:
        c.connection_count = pid_counts.get(c.pid, 0)

    logging.info(f"[DEBUG] Total established connections: {len(connections)}")
    return connections