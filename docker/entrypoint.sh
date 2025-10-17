#!/bin/bash
set -e

# Activate virtual environment if it exists
if [ -d "/app/.venv" ]; then
    source /app/.venv/bin/activate
fi

# Start the Flask server
exec flask run --host=0.0.0.0 --port=5000
