FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy source
COPY ./src /app/src

# Expose service port
EXPOSE 8004

# Set working directory to the services folder to match module import path
WORKDIR /app/src/services

# Default envs (can be overridden by Compose)
ENV POSTGRES_HOST=postgres \
    POSTGRES_PORT=5432 \
    POSTGRES_USER=aipe-tester \
    POSTGRES_PASSWORD=aipe-tester \
    POSTGRES_DB=inulearning

CMD ["uvicorn", "start_ai_service:app", "--host", "0.0.0.0", "--port", "8004"]


