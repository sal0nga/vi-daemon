import sqlite3
import csv
from pathlib import Path

def patch_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Try adding columns if they don't already exist
    try:
        cursor.execute("ALTER TABLE connections ADD COLUMN cpu_percent REAL")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE connections ADD COLUMN memory_rss INTEGER")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

DB_PATH = Path.home() / '.vi' / 'logs' / 'connections.sqlite'
OUTPUT_CSV = Path.home() / '.vi' / 'data' / 'training_data.csv'
OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

def export_training_data():
    patch_schema()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            pid, user, process_name,
            local_port, remote_ip, remote_port,
            cpu_percent, memory_rss, timestamp
        FROM connections
    ''')

    rows = cursor.fetchall()
    conn.close()

    with open(OUTPUT_CSV, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'pid', 'user', 'process_name',
            'local_port', 'remote_ip', 'remote_port',
            'cpu_percent', 'memory_rss', 'timestamp', 'label'
        ])
        for row in rows:
            writer.writerow(list(row) + ['normal'])

if __name__ == '__main__':
    export_training_data()