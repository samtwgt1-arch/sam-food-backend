#!/bin/bash
# 啟動後台服務（不初始化 — 資料已預先包在 Docker image 裡）
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 4 --timeout 120 app:app