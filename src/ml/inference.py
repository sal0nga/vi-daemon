import numpy as np
from .model_loader import load_dummy_model
from keras.models import Model

model: Model = load_dummy_model()

def predict_connection(cpu_percent, memory_rss_mb):
    """Predicts connection behavior: returns 'normal' or 'suspicious'."""
    features = np.array([[cpu_percent, memory_rss_mb]])
    prediction = model.predict(features)
    return "suspicious" if prediction[0][0] > 0.5 else "normal"