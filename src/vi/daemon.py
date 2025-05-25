#!/usr/bin/env python3

# Vi daemon

import sys, os
import warnings
from urllib3.exceptions import NotOpenSSLWarning

# Suppress urllib3 LibreSSL compatibility warnings
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# Ensure the src directory is on Python's module search path
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import time, logging
from pathlib import Path

from vi.system import log_boot_time, log_active_processes
from vi.net_monitor import get_active_connections
from vi.baseline import update_baseline, load_linkage
from vi.connections import tracker
from vi.connections.storage import init_db, insert_connections
from vi.intel import init_intel_db, get_ip_reputation
from vi.behavior import init_behavior_db, check_behavior
from vi.alerts import init_alerts_db, record_alert, send_notification

try: 
    from vi.config import config
except Exception as e:
    logging.error("Configuration error: %s", e)
    sys.exit(1)

log_file = Path.home() / '.vi' / 'logs' / 'vi.log'
log_file.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

from datetime import datetime

# Map anomaly types to severity levels for notifications
ANOMALY_SEVERITY = {
    'new_process': 'low',
    'new_process_port': 'medium',
    'malicious_ip': 'high'
}

# Session-level alert deduplication: tracks when each anomaly was last alerted
_ALERT_HISTORY = {}

def main():
    log_boot_time()
    known_links = load_linkage()
    
    # Initialize the SQLite database for connection logging
    init_db()
    # Initialize the AbuseIPDB cache
    init_intel_db()
    # Initialize the behavioral baseline database
    init_behavior_db()
    # Initialize the alerts database
    init_alerts_db()

    try:
        while True:
            logging.info('--- Snapshot ---')
            log_active_processes()
            connections = get_active_connections()

            # Enrich each connection with IP reputation
            for conn_obj in connections:
                rep = get_ip_reputation(conn_obj.remote_ip)
                conn_obj.reputation_score = rep['score']
                conn_obj.is_malicious = rep['is_malicious']
                
                if rep['is_malicious']:
                    severity = ANOMALY_SEVERITY.get('malicious_ip', 'high')
                    logging.warning(f"Malicious IP detected: {conn_obj.remote_ip} (score={rep['score']})")
                    key = ('malicious_ip', conn_obj.remote_ip)
                    if key not in _ALERT_HISTORY:
                        record_alert(conn_obj, 'malicious_ip', severity=severity)
                        send_notification(
                            "Vi Alert",
                            f"Malicious IP detected: {conn_obj.remote_ip} (score={rep['score']})",
                            severity=severity
                        )
                        _ALERT_HISTORY[key] = datetime.now()

            # Detect behavioral anomalies
            anomalies = check_behavior(connections)
            for co, anomaly in anomalies:
                # Skip “new process” alerts if disabled in config
                if anomaly == 'new_process' and not config.behavior['alert_new_process']:
                    continue
                # Skip “new port” alerts if disabled in config
                if anomaly == 'new_process_port' and not config.behavior['alert_new_process_port']:
                    continue
                severity = ANOMALY_SEVERITY.get(anomaly, 'medium')
                logging.warning(
                    f"Behavioral anomaly [{anomaly}] detected: "
                    f"{co.process_name} (PID {co.pid}) → remote port {co.remote_port}"
                )
                key = (anomaly, co.process_name, co.remote_port)
                if key not in _ALERT_HISTORY:
                    record_alert(co, anomaly, severity=severity)
                    send_notification(
                        "Vi Alert",
                        f"Behavioral anomaly [{anomaly}] detected: "
                        f"{co.process_name} (PID {co.pid}) → remote port {co.remote_port}",
                        severity=severity
                    )
                    _ALERT_HISTORY[key] = datetime.now()
                

            # Persist snapshot of current connections to SQLite
            if config.enable_sqlite_logging:
                insert_connections(connections)

            # Logs new IPs
            update_baseline(connections)

            # Links PID to IP
            tracker.track_connections(connections, known_links)

            time.sleep(config.scan_interval)
    except Exception:
        logging.exception('[DAEMON] Unhandled exception—exiting for launchd to restart.')
        sys.exit(1)

if __name__ == '__main__':
    main()