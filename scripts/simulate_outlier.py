#!/usr/bin/env python3

from src.vi.connections.models import Connection
from src.vi.baseline import update_baseline

# Create a "normal" batch of connections
connections = []

# Simulate normal connections with ~200 seconds duration
for i in range(10):
    conn = Connection(
        pid=1000 + i,
        process_name=f"test_proc_{i}",
        user="tester",
        local_ip="127.0.0.1",
        local_port=5000 + i,
        remote_ip="192.168.1.1",
        remote_port=80,
        status="ESTABLISHED",
        cpu_percent=5.0,
        memory_rss=50 * 1024 * 1024,
        timestamp=None,
        tag="untagged",
        connection_count=1,
        duration_seconds=200,
        is_remote_ipv6=0
    )
    connections.append(conn)

# Add an outlier connection with a very long duration
outlier_conn = Connection(
    pid=9999,
    process_name="evil_proc",
    user="badactor",
    local_ip="127.0.0.1",
    local_port=6000,
    remote_ip="203.0.113.42",
    remote_port=8080,
    status="ESTABLISHED",
    cpu_percent=95.0,
    memory_rss=500 * 1024 * 1024,
    timestamp=None,
    tag="untagged",
    connection_count=1,
    duration_seconds=5000,  # Large duration to force outlier score
    is_remote_ipv6=0
)
connections.append(outlier_conn)

# Run baseline update to compute anomaly scores
update_baseline(connections)

# Print all connections with computed anomaly scores
for conn in connections:
    print(f"Process: {conn.process_name}, PID: {conn.pid}, Duration: {conn.duration_seconds}, Anomaly Score: {conn.anomaly_score}")

print("\nCheck the output — you should see the outlier_conn with a high anomaly score.")