import json
import logging
from pathlib import Path
from datetime import datetime

# Path to baseline data
BASELINE_FILE = Path.home() / ".vi" / "config" / "baseline.json"
LINKAGE_FILE = Path.home() / ".vi" / "config" / "linkage.json"
BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_baseline():
    try:
        if BASELINE_FILE.exists():
            with open(BASELINE_FILE, "r") as f:
                return json.load(f)
        return {"known_ips": []}
    except Exception as e:
        logging.warning(f"[WARN] Failed to  load baseline: {e}")
    return {"known_ips": []}

def load_linkage():
    try:
        if LINKAGE_FILE.exists():
            with open(LINKAGE_FILE, "r") as f:
                data = json.load(f)
                return {
                    tuple(key.split(":", 1)): value
                    for key, value in data.items()
                }
    except Exception as e:
        logging.warning(f"[WARN] Failed to load linkage: {e}")
    return {}

def save_baseline(data):
    with open(BASELINE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_linkage(data):
    with open(LINKAGE_FILE, "w") as f:
        serializable_data = {f"{pid}:{ip}": timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp for (pid, ip), timestamp in data.items()}
        json.dump(serializable_data, f, indent=4)

def update_baseline(connections):
    from vi import tracker

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
    save_linkage(known_links)

    if new_ips:
        updated_ips = sorted(known_ips.union(new_ips))
        save_baseline({"known_ips": updated_ips})