FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements 並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式
COPY . .

# 創建 ChromaDB 資料目錄
RUN mkdir -p /app/chromadb_data

# 暴露端口 (Railway會映射)
EXPOSE 8080

# 啟動命令
CMD ["python", "-c", "import os; from app import app; app.run(host='0.0.0.0', port=8080)"]
