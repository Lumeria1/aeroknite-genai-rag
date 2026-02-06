FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Minimal deps for Stage 2 boot
RUN pip install --no-cache-dir fastapi uvicorn

COPY query_service ./query_service

EXPOSE 8000

CMD ["sh", "-c", "uvicorn query_service.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
