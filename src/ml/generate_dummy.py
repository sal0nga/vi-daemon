from keras.models import Sequential
from keras.layers import Dense
from keras import Input

if __name__ == "__main__":
    import numpy as np
    import os

    X = np.random.rand(500, 2) * 100  # CPU% and memory in MB
    y = (X[:, 0] + X[:, 1] > 100).astype(int)

    model = Sequential([
        Input(shape=(2,)),
        Dense(16, activation='relu'),
        Dense(8, activation='relu'),
        Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(X, y, epochs=10, batch_size=32)

    MODEL_PATH = os.path.expanduser("~/.vi/models/dummy_model.keras")
    os.makedirs(os.path.expanduser("~/.vi/models"), exist_ok=True)
    model.save(MODEL_PATH)
    print("Dummy model saved to", MODEL_PATH)