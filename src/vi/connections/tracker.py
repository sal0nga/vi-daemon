# src/vi/tracker.py

# Maintains map of which PID contacted which IP
import logging
from datetime import datetime
from vi.connections import Connection

# This function is only responsible for tracking and alerting, not for DB insertion logic
# Iterates Connections and builds a key, alerts for new and known links
def track_connections(connections: list[Connection], known_links: dict):
    logging.info("[TRACKER] Tracking process-IP linkage...")
    logging.debug(f"[TRACKER] Known links before processing: {known_links}")

    for conn in connections:
        logging.debug(f"[TRACKER] Processing connection with timestamp: {conn.timestamp}")
        key = (conn.pid, conn.remote_ip, conn.timestamp)

        # Alerting logic: track if a (PID, IP, timestamp) combination has been seen before
        if key not in known_links:
            known_links[key] = datetime.now()
            logging.info(f"[NEW LINK] PID {conn.pid} ({conn.process_name}) -> {conn.remote_ip}")
        else:
            logging.debug(f"[KNOWN LINK] PID {conn.pid} -> {conn.remote_ip}")