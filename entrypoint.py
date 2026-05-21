#!/usr/bin/env python3
import subprocess

print("Starting gunicorn on port 5000")
subprocess.run([
    "gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "app:app"
])