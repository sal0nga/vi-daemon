import json
import logging
from pathlib import Path
from datetime import datetime

# Path to baseline data
BASELINE_FILE = Path.home() / ".vi" / "config" / "baseline.json"
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

def save_baseline(data):
    with open(BASELINE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def update_baseline(connections):
    baseline = load_baseline()
    known_ips = set(baseline.get("known_ips", []))
    new_ips = set()

    logging.info(f"[DEBUG] Total connections received: {len(connections)}")

    for conn in connections:
        raddr = conn.raddr if conn.raddr else None
        if raddr:
            ip = conn.raddr.split(':')[0]
            logging.info(f"[DEBUG] Outbound connection to: {ip}")
            if ip not in known_ips:
                new_ips.add(ip)
                logging.info(f"[!] New outbound IP detected: {ip} at {datetime.now()}")

    if new_ips:
        updated_ips = sorted(known_ips.union(new_ips))
        save_baseline({"known_ips": updated_ips})