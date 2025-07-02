# Manages Vi's baseline of seen outbound IPs and the persisted mapping of PID to IPs.

from vi.config import config
# Manages Vi's baseline of seen outbound IPs and the persisted mapping of PID to IPs.

import json
import logging
from pathlib import Path
from datetime import datetime

# Define anomaly threshold from settings
ANOMALY_STDDEV_THRESHOLD = config.anomaly['stddev_threshold']

# Path to baseline data
BASELINE_FILE = Path.home() / ".vi" / "config" / "baseline.json"
LINKAGE_FILE = Path.home() / ".vi" / "config" / "linkage.json"
BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)

# Reads baseline.json and/or returns list of known IPs
def load_baseline():
    try:
        if BASELINE_FILE.exists():
            with open(BASELINE_FILE, "r") as f:
                return json.load(f)
        return {"known_ips": []}
    except Exception as e:
        logging.warning(f"[WARN] Failed to  load baseline: {e}")
    return {"known_ips": []}

# Reads linkage.json, deserializes its keys into (PID, IP, TS) tuples w/ timestamps 
def load_linkage():
    try:
        if LINKAGE_FILE.exists():
            with open(LINKAGE_FILE, "r") as f:
                data = json.load(f)
                return {
                    # Keys are formatted as "pid:ip:ts", split on last two colons to get tuple
                    tuple(key.rsplit(":", 2)): value
                    for key, value in data.items()
                }
    except Exception as e:
        logging.warning(f"[WARN] Failed to load linkage: {e}")
    return {}

# Writes baseline dict back into baseline.json
def save_baseline(data):
    with open(BASELINE_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Serializes (PID, IP) w/ timestamps into linkage.json
def save_linkage(data):
    with open(LINKAGE_FILE, "w") as f:
        serializable_data = {
            f"{pid}:{ip}:{ts}": timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp
            for (pid, ip, ts), timestamp in data.items()
        }
        json.dump(serializable_data, f, indent=4)

# Logs outbound IPs & alerts for new ones
def update_baseline(connections):
    from vi.connections import tracker

    baseline = load_baseline()
    known_ips = set(baseline.get("known_ips", []))
    new_ips = set()

    known_links = load_linkage()

    logging.info(f"[DEBUG] Total connections received: {len(connections)}")

    for conn in connections:
        ip = getattr(conn, "remote_ip", None)
        if ip:
            logging.info(f"[DEBUG] Outbound connection to: {ip}")
            if ip not in known_ips:
                new_ips.add(ip)
                logging.info(f"[!] New outbound IP detected: {ip} at {datetime.now()}")

    tracker.track_connections(connections, known_links)

    # Compute anomaly_score for each connection based on duration
    for conn in connections:
        try:
            if conn.duration_seconds is not None and conn.connection_count is not None:
                mean_duration = sum(c.duration_seconds for c in connections if c.duration_seconds is not None) / len(connections)
                stddev_duration = (sum((c.duration_seconds - mean_duration) ** 2 for c in connections if c.duration_seconds is not None) / len(connections)) ** 0.5
                if stddev_duration > 0:
                    z_score = (conn.duration_seconds - mean_duration) / stddev_duration
                    conn.anomaly_score = round(abs(z_score), 4)
                else:
                    conn.anomaly_score = 0.0
            else:
                conn.anomaly_score = 0.0
        except Exception as e:
            logging.warning(f"[WARN] Failed to compute anomaly score for PID {getattr(conn, 'pid', 'unknown')}: {e}")

    save_linkage(known_links)

    if new_ips:
        updated_ips = sorted(known_ips.union(new_ips))
        save_baseline({"known_ips": updated_ips})