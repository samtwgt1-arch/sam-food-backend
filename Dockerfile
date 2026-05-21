FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /tmp/chromadb_data

#  Railway 會自動設定 PORT 環境變量
# gunicorn 會綁定到 $PORT
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT:-5000}", "--workers", "2", "--threads", "4", "app:app"]
