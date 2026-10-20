# Dockerfile V5 - Deploy Ready
# hash 2d1e37ec7288c756
# Allocation: SCB 22.4% DELTA 22.4% ADVANC 20.6% PTTEP 20.6% PTT 14.0%

FROM python:3.11-slim

# ติดตั้ง timezone Asia/Bangkok
RUN apt-get update && apt-get install -y --no-install-recommends tzdata && \
    ln -fs /usr/share/zoneinfo/Asia/Bangkok /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements ก่อนเพื่อ cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ทั้งโปรเจค
COPY . .

# สร้างโฟลเดอร์ data ถ้ายังไม่มี (สำหรับ LOG_DIR)
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

# Expose port (Railway จะ inject PORT เอง)
EXPOSE 8000

# Healthcheck (แก้ #5 stale check)
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import requests,os; import sys; p=os.getenv('PORT','8000'); r=requests.get(f'http://localhost:{p}/health',timeout=5); sys.exit(0 if r.status_code==200 else 1)" || exit 1

# Start (ใช้ Procfile ถ้ามี ไม่งั้น main.py)
CMD ["python", "main.py"]
