from src.ml.inference import predict_connection
from src.vi.connections.models import Connection
from datetime import datetime

# Simulated connection
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
    status="ESTABLISHED"
)

tag = predict_connection(conn.cpu_percent, conn.memory_rss)
print(f"Inference result: {tag}")