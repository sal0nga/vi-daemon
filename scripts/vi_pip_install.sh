#!/bin/bash

# Activate Vi's virtual environment
source "$HOME/.vi/.venv/bin/activate"

# Install the specified package(s)
pip install "$@"

# Freeze the current package list to requirements.text
pip freeze > "$HOME/.vi/requirements.txt"

echo "[✓] Installed $* and updated requirements.txt."