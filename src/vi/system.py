# src/vi/system.py

# Simplifies utilities for logging system info
import psutil
import logging
from datetime import datetime

# Fetches OS boot timestamp w/ psutil
def log_boot_time():
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    logging.info(f'Boot Time: {boot_time}')

# Logs PID and name for running processes
def log_active_processes():
    logging.info('Active Processes:')
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            logging.info(f'     PID: {proc.info["pid"]}, Name: {proc.info["name"]}')
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue