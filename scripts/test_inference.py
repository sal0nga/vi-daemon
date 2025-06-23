import sys
import os
sys.path.insert(0, os.path.expanduser("~/.vi/src"))

from src.ml.inference import predict_connection
from src.vi.connections.models import Connection
from datetime import datetime

# Test: Full inference pipeline + schema validation
conn = Connection(
    pid=1234,
    user="test_user",
    process_name="TestProcess",
    local_ip="127.0.0.1",
    local_port=12345,
    remote_ip="8.8.8.8",
    remote_port=443,
    cpu_percent=12.7,
    memory_rss=104857600,  # 100 MB
    timestamp=datetime.now(),
    status="ESTABLISHED",
    connection_count=1,
    duration_seconds=0.0,
    is_remote_ipv6=0
)

memory_rss_mb = conn.memory_rss / (1024 * 1024) if conn.memory_rss is not None else 0.0
tag = predict_connection(
    conn.cpu_percent,
    memory_rss_mb,
    conn.connection_count,
    conn.duration_seconds,
    conn.is_remote_ipv6
)
print(f"Inference result: {tag}")

# Test: Schema validation with bad input
try:
    bad_features = {
        "cpu_percent": "not_a_float",
        "memory_rss_mb": 100.0,
        "connection_count": 2,
        "duration_seconds": 10.0,
        "is_remote_ipv6": 0
    }
    predict_connection(**bad_features)
except Exception as e:
    print(f"Schema validation error (expected): {e}")