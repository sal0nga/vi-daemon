#!/usr/bin/env python3

import psutil
import time
import logging
import subprocess
import re
from datetime import datetime
from pathlib import Path
from collections import namedtuple

from vi_baseline import update_baseline

# Define log file location
log_file = Path.home() / '.vi' / 'logs' / 'vi.log'
log_file.parent.mkdir(parents=True, exist_ok=True)

# Set up logging
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def log_boot_time():
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    logging.info(f'Boot Time: {boot_time}')

def log_active_processes():
    logging.info('Active Processes:')
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            logging.info(f'     PID: {proc.info["pid"]}, Name: {proc.info["name"]}')
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

Connection = namedtuple('Connection', ['laddr', 'raddr', 'status'])

def log_network_connections():
    logging.info('Network Connections (via lsof):')
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

            if '->' in name_field:
                laddr, raddr = name_field.split('->')
                conn = Connection(laddr=laddr, raddr=raddr, status='ESTABLISHED')
                logging.info(f'     {conn.status}: {conn.laddr} -> {conn.raddr}')
                connections.append(conn)
    
    except Exception as e:
        logging.warning(f"[WARN] Failed to read connections via lsof: {e}")

    logging.info(f"[DEBUG] Total Established connections: {len(connections)}")
    return connections

def main():
    log_boot_time()
    while True:
        logging.info('--- Snapshot ---')
        log_active_processes()
        connections = log_network_connections()
        update_baseline(connections)
        time.sleep(10)

if __name__ == '__main__':
    main()