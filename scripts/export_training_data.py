import sqlite3
import csv
from pathlib import Path
from datetime import datetime

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
LAST_EXPORT_PATH = Path.home() / '.vi' / 'data' / 'last_export_timestamp.txt'

def export_training_data():
    patch_schema()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Read the last export timestamp
    last_export = None
    if LAST_EXPORT_PATH.exists():
        with open(LAST_EXPORT_PATH, 'r') as f:
            last_export = f.read().strip()
    print(f"[DEBUG] Last export timestamp: {last_export}")

    # Query and print the most recent timestamp in the DB
    cursor.execute('SELECT MAX(timestamp) FROM connections')
    max_db_ts = cursor.fetchone()[0]
    print(f"[DEBUG] Latest timestamp in DB: {max_db_ts}")

    # Query with optional timestamp filtering
    if last_export:
        cursor.execute('''
            SELECT
                pid, user, process_name,
                local_port, remote_ip, remote_port,
                cpu_percent, memory_rss, timestamp
            FROM connections
            WHERE timestamp >= ?
        ''', (last_export,))
    else:
        cursor.execute('''
            SELECT
                pid, user, process_name,
                local_port, remote_ip, remote_port,
                cpu_percent, memory_rss, timestamp
            FROM connections
        ''')

    rows = cursor.fetchall()
    print(f"[DEBUG] Retrieved {len(rows)} new records.")
    if rows:
        print(f"[DEBUG] Latest timestamp in new records: {max(row[8] for row in rows)}")
    if not rows:
        conn.close()
        # Still update the timestamp if the DB has a max timestamp
        if max_db_ts:
            try:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if max_db_ts <= now_str:
                    with open(LAST_EXPORT_PATH, 'w') as f:
                        f.write(max_db_ts)
                    print(f"[DEBUG] Updated last export timestamp to: {max_db_ts} (no new rows)")
                else:
                    print(f"[WARNING] Skipped updating timestamp. max_db_ts ({max_db_ts}) is in the future.")
            except Exception as e:
                print(f"[ERROR] Failed to write last export timestamp: {e}")
        return

    latest_ts = max(datetime.strptime(row[8], "%Y-%m-%d %H:%M:%S") for row in rows).strftime("%Y-%m-%d %H:%M:%S")
    conn.close()

    # Append to the CSV file
    write_header = not OUTPUT_CSV.exists()
    with open(OUTPUT_CSV, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow([
                'pid', 'user', 'process_name',
                'local_port', 'remote_ip', 'remote_port',
                'cpu_percent', 'memory_rss_mb', 'timestamp', 'label'
            ])
        for row in rows:
            row = list(row)
            if row[7] is not None:  # memory_rss is the 8th item (index 7)
                row[7] = round(row[7] / (1024 * 1024), 2)  # Convert bytes to MB
            writer.writerow(row + ['normal'])

    # Save the new last export timestamp using the latest timestamp from the rows,
    # but only if it's not in the future
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if latest_ts <= now_str:
            with open(LAST_EXPORT_PATH, 'w') as f:
                f.write(latest_ts)
            print(f"[DEBUG] Updated last export timestamp to: {latest_ts}")
        else:
            print(f"[WARNING] Skipped updating timestamp. latest_ts ({latest_ts}) is in the future.")
    except Exception as e:
        print(f"[ERROR] Failed to write last export timestamp: {e}")

if __name__ == '__main__':
    export_training_data()