# Aeroknite GenAI RAG

Enterprise-grade Retrieval-Augmented Generation (RAG) system for Aeroknite
internal drone specifications, engineering documents, reports, policies and business knowledge.

## Quickstart (Run Local)

Prereqs: Docker Desktop (WSL2 integration enabled)

Run locally in WSL:

```bash
## Start stack
make dev

## Testing

make test

## Confirm services
make ps

## Healthcheck
curl http://localhost:8000/health
curl http://localhost:8000/ready

## Stop
make down

## Architecture

See docs/ARCHITECTURE.md.

## Deployment

See docs/DEPLOYMENT.md.
```
