import numpy as np
from .model_loader import load_dummy_model
from keras.models import Model

model: Model = load_dummy_model()

def predict_connection(cpu_percent, memory_rss_mb, connection_count, duration_seconds, is_remote_ipv6):
    """
    Predicts connection behavior: returns 'normal' or 'suspicious'.
    Arguments:
        cpu_percent: float, CPU usage percentage.
        memory_rss_mb: float, memory usage in MB.
        connection_count: int, number of concurrent connections for the process.
        duration_seconds: float, duration of the connection in seconds.
        is_remote_ipv6: int (0 or 1), flag for whether remote IP is IPv6.
    """
    features = np.array([[cpu_percent, memory_rss_mb, connection_count, duration_seconds, is_remote_ipv6]])
    prediction = model.predict(features)
    return "suspicious" if prediction[0][0] > 0.5 else "normal"