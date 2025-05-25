# src/vi/net_monitor.py

# Discovers all current TCP/UDP connections w/ lsof
import subprocess
import re
import logging
from connections import Connection

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

            local, remote = name_field.split('->')
            l_ip, l_port = local.rsplit(':', 1)
            r_ip, r_port = remote.rsplit(':', 1)

            conn = Connection(
                pid=int(pid),
                process_name=name,
                user=user,
                local_ip=l_ip,
                local_port=int(l_port),
                remote_ip=r_ip,
                remote_port=int(r_port),
                status='ESTABLISHED'
            )

            logging.info(f'     {conn}')
            connections.append(conn)

    except Exception as e:
        logging.warning(f"[WARN] Failed to read connections via lsof: {e}")

    logging.info(f"[DEBUG] Total established connections: {len(connections)}")
    return connections