import numpy as np
from .model_loader import load_dummy_model
from keras.models import Model
from pydantic import ValidationError
from vi.connections.schemas import ConnectionFeatures # BaseModel & Field from schemas

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


    try:
        validated = ConnectionFeatures(
            cpu_percent=cpu_percent,
            memory_rss_mb=memory_rss_mb,
            connection_count=connection_count,
            duration_seconds=duration_seconds,
            is_remote_ipv6=is_remote_ipv6
        )
    except ValidationError as e:
        raise ValueError(f"Invalid input features: {e}") from e

    features = np.array([[
        validated.cpu_percent,
        validated.memory_rss_mb,
        validated.connection_count,
        validated.duration_seconds,
        validated.is_remote_ipv6
    ]])
    if features.shape != (1, 5):
        raise ValueError(f"Invalid input shape: expected (1, 5), got {features.shape}")
    prediction = model.predict(features)
    return "suspicious" if prediction[0][0] > 0.5 else "normal"


if __name__ == "__main__":
    import numpy as np

    # Example test feature set: [cpu_percent, memory_rss_mb, connection_count, duration_seconds, is_remote_ipv6]
    test_features = np.array([[0.05, 50.0, 2, 300.0, 0]])
    print("Input shape:", test_features.shape)

    try:
        prediction = model.predict(test_features)
        print("Prediction:", prediction)
    except Exception as e:
        print(f"Model prediction failed: {e}")