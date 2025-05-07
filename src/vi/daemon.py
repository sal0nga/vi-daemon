#!/usr/bin/env python3

import time
import logging
from pathlib import Path
from datetime import datetime

from vi.system import log_boot_time, log_active_processes
from vi.net_monitor import get_active_connections
from vi.vi_baseline import update_baseline

log_file = Path.home() / '.vi' / 'logs' / 'vi.log'
log_file.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def main():
    log_boot_time()
    while True:
        logging.info('--- Snapshot ---')
        log_active_processes()
        connections = get_active_connections()
        update_baseline(connections)
        time.sleep(10)

if __name__ == '__main__':
    main()