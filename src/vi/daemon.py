#!/usr/bin/env python3

# Ensure vi module is found when running under launchd
import sys
import os
sys.path.append(os.path.expanduser("~/.vi/src"))

# Standard Library
import sys, os, time, logging, warnings
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

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
from ml.inference import predict_connection

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
    try:
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    except Exception:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        logging.warning("[LOGGING] Failed to write to file; logging to stdout instead.")

def initialize_databases():
    init_db()
    init_intel_db()
    init_behavior_db()
    init_alerts_db()

# Main loop:
# 1. Logs system boot time and active processes.
# 2. Retrieves active network connections.
# 3. Tracks connection durations and stores their start time.
# 4. Queries IP reputation and applies ML predictions.
# 5. Detects anomalies and logs alerts.
# 6. Saves results to SQLite and updates baselines.
# 7. Sleeps and repeats.

def main():
    # Set up log formatting and output file
    configure_logging()
    
    # Log critical configuration values
    logging.info("[BOOT] Vi Configuration:")
    logging.info(f"    Scan Interval: {config.scan_interval} seconds")
    logging.info(f"    SQLite Logging: {'Enabled' if config.enable_sqlite_logging else 'Disabled'}")
    logging.info(f"    Alert on New Process: {config.behavior.get('alert_new_process', False)}")
    logging.info(f"    Alert on New Process-Port Pair: {config.behavior.get('alert_new_process_port', False)}")
    
    # Log the system boot timestamp
    log_boot_time()
    # Load previously seen PID-IP mappings
    known_links = load_linkage()
    # Set up SQLite databases for alerts, behavior, and intel
    initialize_databases()
    last_stats_time = datetime.now()

    from collections import defaultdict

    # Track connection start times in-memory for duration calculation
    _start_times: dict[Tuple[int, str], Optional[datetime]] = defaultdict(lambda: None)

    try:
        # Main monitoring loop
        while True:
            logging.info('--- Snapshot ---')
            # Record currently running processes
            log_active_processes()
            # Pull active network connections using lsof/psutil
            connections = get_active_connections()
            snapshot_time = datetime.now()

            # Assign timestamp and calculate connection duration
            for conn in connections:
                conn.timestamp = snapshot_time
                key = (conn.pid, conn.remote_ip)
                if key not in _start_times or _start_times[key] is None:
                    _start_times[key] = conn.timestamp
                start_time = _start_times.get(key)
                if start_time is not None:
                    conn.duration_seconds = (conn.timestamp - start_time).total_seconds()
                else:
                    conn.duration_seconds = 0.0

            # Assess IP reputation and apply ML tagging
            for conn_obj in connections:
                try:
                    rep = get_ip_reputation(conn_obj.remote_ip)
                    conn_obj.reputation_score = rep['score']
                    conn_obj.is_malicious = rep['is_malicious']
                except Exception as e:
                    logging.exception(f"[INTEL] Failed to retrieve reputation for IP {conn_obj.remote_ip}")
                    conn_obj.reputation_score = 0.0
                    conn_obj.is_malicious = False

                # ML Predictions
                try:
                    memory_rss_mb = (conn_obj.memory_rss or 0) / (1024 * 1024)
                    conn_obj.tag = predict_connection(
                        conn_obj.cpu_percent or 0.0,
                        memory_rss_mb,
                        conn_obj.connection_count or 0,
                        conn_obj.duration_seconds or 0.0,
                        conn_obj.is_remote_ipv6 or 0
                    )
                    logging.debug(
                        f"[ML] Tag={conn_obj.tag} | PID={conn_obj.pid}, CPU={conn_obj.cpu_percent}, "
                        f"MEM_MB={memory_rss_mb:.2f}, ConnCount={conn_obj.connection_count}, "
                        f"Duration={conn_obj.duration_seconds}, IPv6={conn_obj.is_remote_ipv6}"
                    )
                except Exception:
                    logging.exception(f"[ML] Prediction failed for PID {conn_obj.pid}")
                    conn_obj.tag = "error"

                # Alert and log if IP is flagged as malicious
                try:
                    if getattr(conn_obj, "is_malicious", False):
                        severity = ANOMALY_SEVERITY['malicious_ip']
                        logging.warning(f"Malicious IP detected: {conn_obj.remote_ip} (score={getattr(conn_obj, 'reputation_score', 0.0)})")
                        key = ('malicious_ip', conn_obj.remote_ip)
                        if key not in _ALERT_HISTORY:
                            record_alert(conn_obj, 'malicious_ip', severity=severity)
                            send_notification("Vi Alert", f"Malicious IP detected: {conn_obj.remote_ip} (score={getattr(conn_obj, 'reputation_score', 0.0)})", severity=severity)
                            _ALERT_HISTORY[key] = datetime.now()
                except Exception:
                    logging.exception(f"[ALERT] Failed while handling malicious IP alert for {conn_obj.remote_ip}")

            # Run behavioral anomaly checks
            try:
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
            except Exception:
                logging.exception("[BEHAVIOR] Exception occurred while checking for behavioral anomalies")

            # Persist snapshot to SQLite if logging is enabled
            if config.enable_sqlite_logging:
                try:
                    insert_connections(connections)
                except Exception:
                    logging.exception("[SQLITE] Failed to insert connections into the database")

            # Update known IPs and linkage for future comparisons
            try:
                update_baseline(connections)
                tracker.track_connections(connections, known_links)
            except Exception:
                logging.exception("[BASELINE] Failed to update baseline or track connection linkage")

            # Periodically recompute and store baseline stats every 5 minutes
            if (datetime.now() - last_stats_time).total_seconds() >= 300:
                try:
                    from vi.connections.storage import compute_and_store_baseline_stats
                    compute_and_store_baseline_stats()
                    last_stats_time = datetime.now()
                    logging.info("[BASELINE] Baseline stats recomputed and stored")
                except Exception:
                    logging.exception("[BASELINE] Failed to recompute or store baseline stats")

            time.sleep(config.scan_interval)
    
    except Exception:
        logging.exception('[DAEMON] Unhandled exception—exiting for launchd to restart.')
        sys.exit(1)

if __name__ == '__main__':
    main()