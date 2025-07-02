import sqlite3
from pathlib import Path
from datetime import datetime
import logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.FileHandler(Path.home() / '.vi' / 'logs' / 'vi.stdout.log')
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

# Path to the SQLite database for connection logs
DB_PATH = Path.home() / '.vi' / 'logs' / 'connections.sqlite'

def init_baseline_table():
    """Ensure the baseline_stats table exists."""
    db_conn = sqlite3.connect(DB_PATH)
    c = db_conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS baseline_stats (
            feature_name TEXT PRIMARY KEY,
            mean REAL,
            stddev REAL,
            last_updated TEXT
        )
    ''')
    db_conn.commit()
    db_conn.close()

def init_db():
    """Initialize the SQLite database and ensure the connections table exists."""
    db_conn = sqlite3.connect(DB_PATH)
    c = db_conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS connections (
            timestamp TEXT,
            pid INTEGER,
            user TEXT,
            process_name TEXT,
            local_ip TEXT,
            local_port INTEGER,
            remote_ip TEXT,
            remote_port INTEGER,
            cpu_percent REAL,
            memory_rss INTEGER,
            connection_count INTEGER,
            duration_seconds REAL,
            is_remote_ipv6 INTEGER,
            status TEXT,
            tag TEXT,
            anomaly_score REAL
        )
    ''')
    db_conn.commit()
    db_conn.close()
    init_baseline_table()

def insert_connections(connections):
    """Insert a list of Connection objects into the connections table."""
    if not connections:
        return
    logger.debug(f"[DB] Inserting {len(connections)} connection(s) into the database.")
    db_conn = sqlite3.connect(DB_PATH)
    c = db_conn.cursor()
    for conn_obj in connections:
        try:
            logger.debug(f"Inserting connection PID {conn_obj.pid} - CPU: {conn_obj.cpu_percent}%, Mem: {conn_obj.memory_rss} MB, Tag: {conn_obj.tag}")
            c.execute('''
                INSERT INTO connections (
                    timestamp, pid, user, process_name,
                    local_ip, local_port, remote_ip, remote_port,
                    cpu_percent, memory_rss, connection_count, duration_seconds,
                    is_remote_ipv6, status, tag, anomaly_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                conn_obj.timestamp,
                conn_obj.pid,
                conn_obj.user,
                conn_obj.process_name,
                conn_obj.local_ip,
                conn_obj.local_port,
                conn_obj.remote_ip,
                conn_obj.remote_port,
                conn_obj.cpu_percent,
                conn_obj.memory_rss,
                conn_obj.connection_count,
                conn_obj.duration_seconds,
                conn_obj.is_remote_ipv6,
                conn_obj.status,
                conn_obj.tag,
                conn_obj.anomaly_score
            ))
            print(f"Inserted connection: {conn_obj}")
        except Exception as e:
            print(f"Error inserting connection {conn_obj}: {e}")
    db_conn.commit()
    db_conn.close()
def compute_and_store_baseline_stats():
    """Compute mean and stddev for relevant features and store them in baseline_stats table."""
    import numpy as np

    db_conn = sqlite3.connect(DB_PATH)
    c = db_conn.cursor()

    features = ['cpu_percent', 'memory_rss', 'connection_count', 'duration_seconds']
    for feature in features:
        try:
            c.execute(f"SELECT {feature} FROM connections WHERE {feature} IS NOT NULL")
            values = [row[0] for row in c.fetchall() if row[0] is not None]
            if not values:
                logger.warning(f"[BASELINE] No data for feature: {feature}")
                continue

            mean_val = np.mean(values)
            stddev_val = np.std(values)
            last_updated = datetime.now().isoformat()

            c.execute('''
                INSERT INTO baseline_stats (feature_name, mean, stddev, last_updated)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(feature_name) DO UPDATE SET
                    mean=excluded.mean,
                    stddev=excluded.stddev,
                    last_updated=excluded.last_updated
            ''', (feature, mean_val, stddev_val, last_updated))

            logger.debug(f"[BASELINE] Stats updated for {feature}: mean={mean_val:.2f}, stddev={stddev_val:.2f}")

        except Exception as e:
            logger.error(f"[BASELINE] Failed to compute stats for {feature}: {e}")

    db_conn.commit()
    db_conn.close()