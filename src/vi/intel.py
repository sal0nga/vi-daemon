import sqlite3, time, requests
from pathlib import Path
from vi.config import config
import logging

DB_PATH = Path.home() / '.vi' / 'logs' / 'intel_cache.sqlite'

def init_intel_db():
    """Create the cache table for IP reputations."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS ip_reputation (
        ip TEXT PRIMARY KEY,
        last_checked REAL,
        score INTEGER,
        is_malicious INTEGER
    )
    """)
    conn.commit()
    conn.close()

def get_ip_reputation(ip: str) -> dict:
    """Returns {'score': int, 'is_malicious': bool}, using cache or AbuseIPDB."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = time.time()
    # Check cache (recompute malicious against current threshold)
    c.execute("SELECT last_checked, score FROM ip_reputation WHERE ip=?", (ip,))
    row = c.fetchone()
    if row and (now - row[0]) < config.intel['cache_ttl']:
        raw_score = row[1]
        is_m = raw_score >= config.intel['threshold_score']
        conn.close()
        return {'score': raw_score, 'is_malicious': is_m}

    # Query AbuseIPDB
    logging.info(f"Querying AbuseIPDB for {ip}")
    try:
        headers = {
            'Key': config.intel['abuseipdb_api_key'],
            'Accept': 'application/json'
        }
        resp = requests.get(
            'https://api.abuseipdb.com/api/v2/check',
            params={'ipAddress': ip},
            headers=headers
        )
        resp.raise_for_status()
        data = resp.json()['data']
        score = data.get('abuseConfidenceScore', 0)
        is_mal = score >= config.intel['threshold_score']
        # Debug: log threshold comparison
        logging.info(
            f"AbuseIPDB: IP={ip}, score={score}, threshold={config.intel['threshold_score']}, is_malicious={is_mal}"
        )
    except Exception as e:
        logging.error(f"AbuseIPDB lookup failed for {ip}: {e}")
        # Fallback to safe defaults on error
        score = 0
        # Determine malicious flag based on configured threshold even on error
        is_mal = score >= config.intel['threshold_score']
        # Debug: log threshold comparison on error path
        logging.info(
            f"AbuseIPDB (error path): IP={ip}, score={score}, threshold={config.intel['threshold_score']}, is_malicious={is_mal}"
        )

    # Update cache
    c.execute("""
      REPLACE INTO ip_reputation (ip, last_checked, score)
      VALUES (?, ?, ?)
    """, (ip, now, score))
    conn.commit()
    conn.close()
    return {'score': score, 'is_malicious': is_mal}