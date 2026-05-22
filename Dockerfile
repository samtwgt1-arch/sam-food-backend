FROM python:3.11-slim

ENV CHROMA_DATA_PATH=/app/chromadb_data
ENV CHROMA_CACHE_PATH=/app/.cache

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製已初始化的 ChromaDB 資料庫（含 12 家餐廳預嵌入向量）
COPY chromadb_data/ /app/chromadb_data/

# 複製預下載的嵌入模型（all-MiniLM-L6-v2），避免啟動時下載
COPY .cache/ /app/.cache/

COPY . .

EXPOSE 5000

# 直接啟動 gunicorn（資料已預先初始化，無需額外設定）
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "120", "app:app"]