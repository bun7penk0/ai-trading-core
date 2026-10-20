FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && if [ -s requirements.txt ]; then pip install -r requirements.txt; fi
COPY . .
EXPOSE 8000
CMD ["sh", "-c", "python main.py"]
