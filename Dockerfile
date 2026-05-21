FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/chromadb_data

# Let Railway set the PORT - just run the app
CMD ["python", "app.py"]
