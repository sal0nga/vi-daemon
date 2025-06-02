from keras.models import Sequential
from keras.layers import Dense
from keras import Input

if __name__ == "__main__":
    import numpy as np
    import os

    # Generate five features: CPU% (0-100), memory in MB (0-100), connection_count (0-10), duration_seconds (0-100), is_remote_ipv6 (0 or 1)
    cpu = np.random.rand(500, 1) * 100
    mem = np.random.rand(500, 1) * 100
    conn_count = np.random.randint(0, 11, size=(500, 1))
    duration = np.random.rand(500, 1) * 100
    ipv6 = np.random.randint(0, 2, size=(500, 1))
    X = np.hstack([cpu, mem, conn_count, duration, ipv6])
    # Simple labeling logic: if CPU + mem + conn_count*10 + duration > 150 or is remote IPv6, mark as suspicious
    y = (((cpu[:, 0] + mem[:, 0] + conn_count[:, 0] * 10 + duration[:, 0]) > 150) | (ipv6[:, 0] == 1)).astype(int)

    model = Sequential([
        Input(shape=(5,)),
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