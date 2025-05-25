import numpy as np
from .model_loader import load_dummy_model
from keras.models import Model

model: Model = load_dummy_model()

def run_inference(cpu_percent, memory_rss_mb):
    """Returns 'normal' or 'suspicious' based on model prediction."""
    features = np.array([[cpu_percent, memory_rss_mb]])
    prediction = model.predict(features)
    return "suspicious" if prediction[0][0] > 0.5 else "normal"