import sqlite3
from pathlib import Path
from datetime import datetime

# Path to the SQLite database for connection logs
DB_PATH = Path.home() / '.vi' / 'logs' / 'connections.sqlite'

def init_db():
    """Initialize the SQLite database and ensure the connections table exists."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS connections (
            timestamp TEXT,
            pid INTEGER,
            user TEXT,
            process_name TEXT,
            local_ip TEXT,
            local_port INTEGER,
            remote_ip TEXT,
            remote_port INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def insert_connections(connections):
    """Insert a list of Connection objects into the connections table."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for conn_obj in connections:
        c.execute('''
            INSERT INTO connections (
                timestamp, pid, user, process_name,
                local_ip, local_port, remote_ip, remote_port
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            conn_obj.pid,
            conn_obj.user,
            conn_obj.process_name,
            conn_obj.local_ip,
            conn_obj.local_port,
            conn_obj.remote_ip,
            conn_obj.remote_port
        ))
    conn.commit()
    conn.close()