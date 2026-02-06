FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Stage 2: just keep the container alive deterministically.
COPY ingestion_worker ./ingestion_worker

CMD ["python", "-m", "ingestion_worker.main"]
