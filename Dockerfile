FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

# deps ก่อน เพื่อ cache layer
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# โค้ด
COPY main.py .

# Railway inject PORT — ใช้ sh -c เพื่อให้ $PORT ขยายได้
EXPOSE 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
