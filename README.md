# Vi – AI-Driven macOS Security Assistant

**Vi** is a personal security assistant designed to provide real-time behavioral monitoring, anomaly detection, and AI-based classification of network activity on macOS. It acts as a lightweight, on-device **Intrusion Detection System (IDS)** with future extensibility into full endpoint defense.

---

## 🚀 Overview

Vi monitors outbound network connections and associates them with the processes that generated them. It logs behavior, tracks connection durations, calculates resource usage, and uses machine learning to identify suspicious activity.

---

## 🔐 Key Features

- **Real-time Process & Network Monitoring**  
  Discovers TCP/UDP connections via `lsof` and `psutil`  
  Tracks CPU/memory usage, connection counts, and durations

- **Persistent Behavior Mapping**  
  Logs seen IPs and PID-to-IP mappings with timestamped linkage  
  Establishes behavioral baselines and identifies novel outbound traffic

- **Machine Learning Inference**  
  Supports TensorFlow/Keras model predictions on live traffic  
  Tagging of connections as `normal` or `suspicious`

- **Anomaly Detection & Logging**  
  Logs structured behavioral data for further offline analysis  
  Supports CSV export for model training and validation

- **Built for macOS**  
  Launches as a background daemon via `launchd`  
  Monitors with low system overhead

---

## 🧠 Architecture

```
+------------+     +----------------+     +-------------------+
| net_monitor| --> |  Vi Connection | --> |  ML Inference     |
| (lsof/psutil)    |  Model (object)|     | (TensorFlow/Keras)|
+------------+     +----------------+     +-------------------+
       |                        |
       v                        v
   Baseline Configs       SQLite + CSV Logs
```

---

## 📦 Directory Structure

```
.vi/
├── config/           # Stores baseline.json, linkage.json
├── launch_agents/    # launchd plist for background daemon
├── logs/             # vi.log and connection snapshots
├── scripts/          # export + test scripts
├── src/
│   ├── ml/           # ML inference + dummy model
│   └── vi/
│       ├── connections/    # models.py, schemas.py
│       ├── alerts.py       # (planned)
│       ├── baseline.py
│       ├── behavior.py     # (planned)
│       ├── config.py
│       ├── daemon.py
│       ├── net_monitor.py
│       └── system.py
```

---

## ⚙️ Tech Stack

- Python 3.9+
- `psutil`, `subprocess`, `lsof`
- `tensorflow` / `keras`
- `sqlite3`, `csv`
- `pydantic` (input validation)
- macOS `launchd`

---

## 📈 Status

| Phase   | Description                           | Status     |
|---------|---------------------------------------|------------|
| Phase 1 | System + Network Logging              | ✅ Complete |
| Phase 2 | Baseline + IP Mapping                 | ✅ Complete |
| Phase 3 | TensorFlow Dummy Inference            | ✅ Complete |
| Phase 4 | Robust Logging & Error Handling       | ✅ Complete |
| Phase 5 | Data Export + Schema Validation       | ✅ Complete |
| Phase 6 | Threshold-Based Anomaly Detection     | 🚧 Pending  |
| Phase 7 | Real ML Model Training & Evaluation   | 🚧 Pending  |

---

## 🧪 Example Usage

```bash
python scripts/export_training_data.py
python scripts/test_inference.py
```

Produces labeled CSV data for training and verifies ML inference via schema-validated inputs.

---

## 🔒 Future Goals

- Real model integration (Phase 7+)
- Remote webhook alerting (e.g. Slack, email)
- Voice command interface for querying anomalies
- Live behavior graphing
- Integration with blocklists or threat intel feeds

---

## 👤 Author

**Keenan Salonga**  
Master's in Cybersecurity  
[LinkedIn](https://www.linkedin.com/in/keenansalonga) • [GitHub](https://github.com/krossteil)

---

## 📝 License

MIT License — feel free to fork, extend, and adapt.
