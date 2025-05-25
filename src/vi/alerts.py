""" Alert management module for Vi. 
Handles initialization of alert database, 
recording of alerts, and notification dispatch.
"""

import sqlite3
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from vi.config import config

# Path to the SQLite database for alerts
DB_PATH = Path.home() / '.vi' / 'logs' / 'alerts.sqlite'

def init_alerts_db():
    """Ensure the alerts table exists."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
      CREATE TABLE IF NOT EXISTS alerts (
        timestamp TEXT,
        type TEXT,
        process_name TEXT,
        pid INTEGER,
        remote_ip TEXT,
        remote_port INTEGER,
        severity TEXT
      )
    ''')
    conn.commit()
    conn.close()

def record_alert(conn_obj, anomaly_type, severity='medium'):
    """Persist one alert to SQLite."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
      INSERT INTO alerts (
        timestamp, type, process_name, pid,
        remote_ip, remote_port, severity
      ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
      datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
      anomaly_type,
      conn_obj.process_name,
      conn_obj.pid,
      conn_obj.remote_ip,
      conn_obj.remote_port,
      severity
    ))
    conn.commit()
    conn.close()

def send_notification(title: str, message: str, severity: str = 'medium'):
    # Respect notification settings from config
    # Debug: log notification invocation
    logging.info(f"send_notification called with severity={severity}, config={config.notifications!r}")
    notif_cfg = config.notifications
    if not notif_cfg['enable_desktop']:
        logging.info("Notification skipped: desktop notifications disabled in config")
        return
    if severity != notif_cfg['min_severity']:
        logging.info(f"Notification skipped: severity '{severity}' does not match min_severity '{notif_cfg['min_severity']}'")
        return
    notifier = notif_cfg['notifier']
    logging.info(f"Dispatching notification via '{notifier}'")
    # Fire a macOS banner notification via terminal-notifier
    subprocess.run([
        notifier,
        '-title', title,
        '-message', message
    ])