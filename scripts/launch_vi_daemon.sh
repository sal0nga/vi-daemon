

#!/bin/bash

# Path to the LaunchAgent plist
PLIST_PATH="$HOME/Library/LaunchAgents/com.vi.daemon.plist"

echo "Booting out existing Vi daemon (if any)..."
launchctl bootout gui/$(id -u) "$PLIST_PATH" 2>/dev/null

echo "Bootstrapping Vi daemon..."
launchctl bootstrap gui/$(id -u) "$PLIST_PATH"

echo "Force restarting Vi daemon..."
launchctl kickstart -k gui/$(id -u)/com.vi.daemon

echo "Vi daemon restarted successfully."