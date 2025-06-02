#!/bin/zsh

echo "Attempting to boot out Vi..."

# Boot out the launch agent
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.vi.daemon.plist

# Kill any remaining Python processes related to Vi
pkill -f vi/daemon.py

echo "Vi has been stopped."