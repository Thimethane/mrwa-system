# ============================================================================
# Dockerfile - MRWA Backend Container
# ============================================================================

FROM python:3.12-slim

LABEL maintainer="MRWA Team"
LABEL description="MRWA Backend - Autonomous Research & Workflow Agent"

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        postgresql-client \
        curl \
        build-essential \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*


# Copy Python dependencies
COPY requirements.txt ./

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY core/ ./core/
COPY ingestion/ ./ingestion/
COPY main.py ./
COPY alembic.ini ./
COPY migrations/ ./migrations/

# Copy wait-for-services script
COPY wait-for-services.sh ./wait-for-services.sh
RUN chmod +x ./wait-for-services.sh

# Create non-root user and set ownership
RUN useradd -m -u 1000 mrwa && chown -R mrwa:mrwa $APP_HOME
USER mrwa

# Expose port for FastAPI
EXPOSE 8000

# Healthcheck (optional, will return 1 on failure)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health') or exit(1)"

# Entrypoint: wait for Postgres & Redis before starting Uvicorn
CMD ["./wait-for-services.sh", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
