FROM python:3.11-slim
WORKDIR /app

# Copy requirements ก่อนเพื่อ cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ทั้งโปรเจค
COPY . .

# สร้างโฟลเดอร์ data ถ้ายังไม่มี
RUN mkdir -p /app/data /app/logs

# Environment V5
ENV PYTHONUNBUFFERED=1
ENV CONFIG_PATH=data/LIVE_CONFIG_10K.json
ENV ADAPTIVE_TIERS_PATH=data/ADAPTIVE_TIERS.json
ENV TRADE_LOG_PATH=data/trade_log.json
ENV LOG_DIR=/app/data
ENV PORTFOLIO=10000
ENV TZ=Asia/Bangkok
ENV LIVE_CONFIG_HASH=2d1e37ec7288c756
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Start
CMD ["python", "main.py"]
