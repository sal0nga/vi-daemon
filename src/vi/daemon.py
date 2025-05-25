
#!/usr/bin/env python3

# Ensure vi module is found when running under launchd
import sys
import os
sys.path.append(os.path.expanduser("~/.vi/src"))

# Standard Library
import sys, os, time, logging, warnings
from pathlib import Path
from datetime import datetime

# Third-Party
from urllib3.exceptions import NotOpenSSLWarning

# Internal Imports
from vi.connections import tracker
from vi.alerts import init_alerts_db, record_alert, send_notification
from vi.baseline import update_baseline, load_linkage
from vi.behavior import init_behavior_db, check_behavior
from vi.config import config
from vi.connections.storage import init_db, insert_connections
from vi.net_monitor import get_active_connections
from vi.system import log_boot_time, log_active_processes
from vi.intel import init_intel_db, get_ip_reputation

# Suppress urllib3 LibreSSL compatibility warnings
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# Constants and Configuration
log_file = Path.home() / '.vi' / 'logs' / 'vi.log'
log_file.parent.mkdir(parents=True, exist_ok=True)

ANOMALY_SEVERITY = {
    'new_process': 'low',
    'new_process_port': 'medium',
    'malicious_ip': 'high'
}

_ALERT_HISTORY = {}

def configure_logging():
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def initialize_databases():
    init_db()
    init_intel_db()
    init_behavior_db()
    init_alerts_db()

def main():
    configure_logging()
    log_boot_time()
    known_links = load_linkage()
    initialize_databases()

    try:
        while True:
            logging.info('--- Snapshot ---')
            log_active_processes()
            connections = get_active_connections()
            snapshot_time = datetime.now()

            for conn in connections:
                conn.timestamp = snapshot_time

            for conn_obj in connections:
                rep = get_ip_reputation(conn_obj.remote_ip)
                conn_obj.reputation_score = rep['score']
                conn_obj.is_malicious = rep['is_malicious']

                if rep['is_malicious']:
                    severity = ANOMALY_SEVERITY['malicious_ip']
                    logging.warning(f"Malicious IP detected: {conn_obj.remote_ip} (score={rep['score']})")
                    key = ('malicious_ip', conn_obj.remote_ip)
                    if key not in _ALERT_HISTORY:
                        record_alert(conn_obj, 'malicious_ip', severity=severity)
                        send_notification("Vi Alert", f"Malicious IP detected: {conn_obj.remote_ip} (score={rep['score']})", severity=severity)
                        _ALERT_HISTORY[key] = datetime.now()

            anomalies = check_behavior(connections)
            for co, anomaly in anomalies:
                if anomaly == 'new_process' and not config.behavior['alert_new_process']:
                    continue
                if anomaly == 'new_process_port' and not config.behavior['alert_new_process_port']:
                    continue
                severity = ANOMALY_SEVERITY.get(anomaly, 'medium')
                logging.warning(f"Behavioral anomaly [{anomaly}] detected: {co.process_name} (PID {co.pid}) → remote port {co.remote_port}")
                key = (anomaly, co.process_name, co.remote_port)
                if key not in _ALERT_HISTORY:
                    record_alert(co, anomaly, severity=severity)
                    send_notification("Vi Alert", f"Behavioral anomaly [{anomaly}] detected: {co.process_name} (PID {co.pid}) → remote port {co.remote_port}", severity=severity)
                    _ALERT_HISTORY[key] = datetime.now()

            if config.enable_sqlite_logging:
                insert_connections(connections)

            update_baseline(connections)
            tracker.track_connections(connections, known_links)
            time.sleep(config.scan_interval)
    except Exception:
        logging.exception('[DAEMON] Unhandled exception—exiting for launchd to restart.')
        sys.exit(1)

if __name__ == '__main__':
    main()