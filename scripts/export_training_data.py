import sqlite3
import csv
from pathlib import Path

DB_PATH = Path.home() / '.vi' / 'logs' / 'connections.sqlite'
OUTPUT_CSV = Path.home() / '.vi' / 'data' / 'training_data.csv'
OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

def export_all_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            pid, user, process_name,
            local_port, remote_ip, remote_port,
            cpu_percent, memory_rss, timestamp, status, tag
        FROM connections
    ''')
    rows = cursor.fetchall()
    conn.close()

    with open(OUTPUT_CSV, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'pid', 'user', 'process_name',
            'local_port', 'remote_ip', 'remote_port',
            'cpu_percent', 'memory_rss_mb', 'timestamp', 'status', 'tag'
        ])
        for row in rows:
            row = list(row)
            if row[7] is not None:  # Convert memory_rss from bytes to MB
                row[7] = round(row[7] / (1024 * 1024), 2)
            writer.writerow(row)

if __name__ == '__main__':
    export_all_data()