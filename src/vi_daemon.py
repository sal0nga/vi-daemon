#!/usr/bin/env python3

import psutil
import time
import logging
from datetime import datetime
from pathlib import Path

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

def log_network_connections():
    logging.info('Network Connections:')
    connections = [] # New: collect connection objects

    for conn in psutil.net_connections(kind='inet'):
        laddr = f'{conn.laddr.ip}:{conn.laddr.port}' if conn.laddr else 'N/A'
        raddr = f'{conn.laddr.ip}:{conn.laddr.port}' if conn.laddr else 'N/A'
        logging.info(f'     {conn.status}: {laddr} -> {raddr}')
        connections.append(conn)
    
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