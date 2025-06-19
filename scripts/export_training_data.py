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
            cpu_percent, memory_rss, connection_count, duration_seconds, is_remote_ipv6,
            local_port, remote_ip, remote_port,
            status, tag, timestamp
        FROM connections
    ''')
    rows = cursor.fetchall()
    conn.close()

    with open(OUTPUT_CSV, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'pid', 'user', 'process_name',
            'cpu_percent', 'memory_rss_mb', 'connection_count', 'duration_seconds', 'is_remote_ipv6',
            'local_port', 'remote_ip', 'remote_port',
            'status', 'tag', 'timestamp'
        ])
        for row in rows:
            row = list(row)
            if row[4] is not None:  # Convert memory_rss from bytes to MB
                row[4] = round(row[4] / (1024 * 1024), 2)
            writer.writerow(row)

if __name__ == '__main__':
    export_all_data()