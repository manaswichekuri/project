FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=5001 \
    APP_ENV=production \
    MODEL_DIR=/app/datasets

# curl is used by the container healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run as an unprivileged user
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app/datasets \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 5001

HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=5 \
    CMD curl -fsS http://localhost:${PORT}/api/v1/health || exit 1

# The ML detection run can take a while on large datasets, hence the generous timeout
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers ${GUNICORN_WORKERS:-2} --threads 4 --timeout 120 --access-logfile - wsgi:app"]
