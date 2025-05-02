#!/bin/bash

set -e  # Exit on error

echo "[+] Bootstrapping Vi..."

VI_DIR="$HOME/.vi"
SRC_DIR="$VI_DIR/src"
VENV_DIR="$VI_DIR/.venv"
PLIST_LOCAL="$VI_DIR/launch_agents/com.vi.daemon.plist"
PLIST_TARGET="$HOME/Library/LaunchAgents/com.vi.daemon.plist"

# 1. Create virtual environment if not already present
if [ ! -d "$VENV_DIR" ]; then
    echo "[+] Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# 2. Activate virtual environment and install packages
echo "[+] Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "[+] Installing required packages..."
pip install --upgrade pip
pip install psutil

# 3. Write requirements.txt (optional but useful for reproducibility)
echo "[+] Writing requirements.txt..."
pip freeze > "$VI_DIR/requirements.txt"

# 4. Link the LaunchAgent plist if not already linked
if [ ! -L "$PLIST_TARGET" ]; then
    echo "[+] Linking LaunchAgent plist..."
    ln -s "$PLIST_LOCAL" "$PLIST_TARGET"
fi

# 5. Load the LaunchAgent with launchctl
echo "[+] Loading Vi daemon with launchctl..."
launchctl load "$PLIST_TARGET" 2>/dev/null || echo "[!] LaunchAgent may already be loaded."

echo "[✓] Vi is bootstrapped and ready."
echo "[i] To install additional packages in the future, use ~/.vi/scripts/vi_pip_install.sh <package_name>"