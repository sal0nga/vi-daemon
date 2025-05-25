import os
from keras.models import load_model
from typing import Any

MODEL_PATH = os.path.expanduser("~/.vi/models/dummy_model.keras")

def load_dummy_model() -> Any:
    return load_model(MODEL_PATH)