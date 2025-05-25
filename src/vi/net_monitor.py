# src/vi/net_monitor.py

# Discovers all current TCP/UDP connections w/ lsof
import subprocess
import re
import logging
from connections import Connection
import psutil
import time

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
                cpu = proc.cpu_percent(interval=0.1)
                mem = proc.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                cpu = 0.0
                mem = 0

            local, remote = name_field.split('->')
            l_ip, l_port = local.rsplit(':', 1)
            r_ip, r_port = remote.rsplit(':', 1)

            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

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
                timestamp=timestamp
            )

            logging.info(f'     {conn}')
            connections.append(conn)

    except Exception as e:
        logging.warning(f"[WARN] Failed to read connections via lsof: {e}")

    logging.info(f"[DEBUG] Total established connections: {len(connections)}")
    return connections