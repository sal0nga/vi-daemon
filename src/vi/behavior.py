import sqlite3
from pathlib import Path

# Path to the SQLite database for behavioral baseline
DB_PATH = Path.home() / '.vi' / 'logs' / 'behavior.sqlite'

def init_behavior_db():
    """Ensure the baseline tables exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Record seen process names
    c.execute('''
        CREATE TABLE IF NOT EXISTS seen_process_names (
            process_name TEXT PRIMARY KEY
        )
    ''')
    # Record seen process_name + remote_port pairs
    c.execute('''
        CREATE TABLE IF NOT EXISTS seen_process_ports (
            process_name TEXT,
            remote_port INTEGER,
            PRIMARY KEY (process_name, remote_port)
        )
    ''')
    conn.commit()
    conn.close()

def check_behavior(connections):
    """
    Scan each Connection for anomalies:
      - A process name never seen before.
      - A process contacting a port it hasn't used before.
    Returns a list of (conn_obj, anomaly_type) tuples.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    anomalies = []
    for co in connections:
        # New process name?
        c.execute('SELECT 1 FROM seen_process_names WHERE process_name = ?', (co.process_name,))
        if c.fetchone() is None:
            anomalies.append((co, 'new_process'))
            c.execute('INSERT INTO seen_process_names (process_name) VALUES (?)', (co.process_name,))
        # New port for this process?
        c.execute(
            'SELECT 1 FROM seen_process_ports WHERE process_name = ? AND remote_port = ?',
            (co.process_name, co.remote_port)
        )
        if c.fetchone() is None:
            anomalies.append((co, 'new_process_port'))
            c.execute(
                'INSERT INTO seen_process_ports (process_name, remote_port) VALUES (?, ?)',
                (co.process_name, co.remote_port)
            )
    conn.commit()
    conn.close()
    return anomalies