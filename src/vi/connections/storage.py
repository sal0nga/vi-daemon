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
            memory_rss INTEGER
        )
    ''')
    db_conn.commit()
    db_conn.close()

def insert_connections(connections):
    """Insert a list of Connection objects into the connections table."""
    if not connections:
        return
    # logger.debug(f"[DB] Inserting {len(connections)} connection(s) into the database.")
    db_conn = sqlite3.connect(DB_PATH)
    c = db_conn.cursor()
    for conn_obj in connections:
        try:
            c.execute('''
                INSERT INTO connections (
                    timestamp, pid, user, process_name,
                    local_ip, local_port, remote_ip, remote_port,
                    cpu_percent, memory_rss
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                conn_obj.memory_rss
            ))
            print(f"Inserted connection: {conn_obj}")
        except Exception as e:
            print(f"Error inserting connection {conn_obj}: {e}")
    db_conn.commit()
    db_conn.close()