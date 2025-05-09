#!/usr/bin/env python3

# Vi daemon

import sys, os
# Ensure the src directory is on Python's module search path
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import time, logging
from pathlib import Path

from vi.system import log_boot_time, log_active_processes
from vi.net_monitor import get_active_connections
from vi.baseline import update_baseline, load_linkage
from vi import tracker
from vi.storage import init_db, insert_connections

log_file = Path.home() / '.vi' / 'logs' / 'vi.log'
log_file.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    log_boot_time()
    known_links = load_linkage()
    # Initialize the SQLite database for connection logging
    init_db()
    try:
        while True:
            logging.info('--- Snapshot ---')
            log_active_processes()
            connections = get_active_connections()

            # Persist snapshot of current connections to SQLite
            insert_connections(connections)

            # Logs new IPs
            update_baseline(connections)

            # Links PID to IP
            tracker.track_connections(connections, known_links)

            time.sleep(10)
    except Exception:
        logging.exception('[DAEMON] Unhandled exception—exiting for launchd to restart.')
        sys.exit(1)

if __name__ == '__main__':
    main()