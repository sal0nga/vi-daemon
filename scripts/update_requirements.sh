#!/bin/bash

# Activate the virtual environment
source "$HOME/.vi/.venv/bin/activate"

# Move to project root
cd "$HOME/.vi" || exit

# Freeze current dependencies into requirements.txt
pip freeze > requirements.txt

echo "✅ requirements.txt updated."