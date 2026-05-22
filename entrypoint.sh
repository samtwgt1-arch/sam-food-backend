#!/bin/bash
set -e

echo "=== [entrypoint] Starting initialization ==="

# 初始化資料庫（會觸發 ChromaDB 嵌入模型下載 + 寫入 12 家餐廳資料）
python /app/init_db.py

echo "=== [entrypoint] Starting gunicorn ==="
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 4 --timeout 120 app:app