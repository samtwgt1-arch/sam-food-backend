#!/usr/bin/env python3
import os
import subprocess

port = os.environ.get("PORT", "5000")
print(f"Starting on port {port}")
subprocess.run([
    "gunicorn", "--bind", f"0.0.0.0:{port}", "--workers", "2", "--threads", "4", "app:app"
])