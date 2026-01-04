from fastapi import FastAPI

app = FastAPI(title="Aeroknite Query Service", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict:
    # Stage 2: readiness = process is running.
    # Stage 5+: readiness will validate DB/Redis/model connectivity.
    return {"status": "ready"}
