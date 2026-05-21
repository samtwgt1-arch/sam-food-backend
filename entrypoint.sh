#!/bin/bash
PORT=${PORT:-5000}
echo "Starting on port $PORT"
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 app:app