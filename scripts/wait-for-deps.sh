#!/usr/bin/env bash
set -euo pipefail

# Wait for services to become healthy in docker compose.
# Usage:
#   scripts/wait-for-deps.sh [compose-file]
#
# Notes:
# - Uses docker compose ps -q to avoid hardcoded container names.
# - Fails fast on unhealthy.
# - Dumps logs on timeout/unhealthy.

COMPOSE_FILE="${1:-infra/docker-compose.yml}"
echo "Waiting for docker compose services to be healthy..."
echo "Using compose file: ${COMPOSE_FILE}"

# If a compose file argument was provided, shift it off so any remaining arguments
# are treated as the list of services to wait for.
if (( "$#" > 0 )); then
  COMPOSE_FILE="$1"
  shift
else
  COMPOSE_FILE="infra/docker-compose.yml"
fi

WAIT_FOR_DEPS_TIMEOUT_SECONDS=180  # 3 minutes

# Allow callers to specify services explicitly as additional arguments:
#   scripts/wait-for-deps.sh [compose-file] service1 service2 ...
# If no services are provided, fall back to the existing default list.
if (( "$#" > 0 )); then
  SERVICES_TO_WAIT=("$@")
else
  SERVICES_TO_WAIT=("postgres" "redis" "query-service")
fi
deadline=$((SECONDS + WAIT_FOR_DEPS_TIMEOUT_SECONDS))

for svc in "${SERVICES_TO_WAIT[@]}"; do
  echo "→ Waiting for: ${svc}"

  while true; do
    if (( SECONDS > deadline )); then
      echo "ERROR: Timeout waiting for ${svc} to become healthy"
      docker compose -f "${COMPOSE_FILE}" ps || true
      docker compose -f "${COMPOSE_FILE}" logs --tail=200 "${svc}" 2>&1 || true
      exit 1
    fi

    container_id="$(docker compose -f "${COMPOSE_FILE}" ps -q "${svc}" 2>/dev/null || true)"
    if [[ -z "${container_id}" ]]; then
      echo "  ⏳ Container not started yet..."
      sleep 2
      continue
    fi

    status="$(docker inspect --format='{{.State.Health.Status}}' "${container_id}" 2>/dev/null || echo "unknown")"

    if [[ "${status}" == "healthy" ]]; then
      echo "  ✓ ${svc} is healthy"
      break
    fi

    if [[ "${status}" == "unhealthy" ]]; then
      echo "ERROR: ${svc} is unhealthy"
      docker compose -f "${COMPOSE_FILE}" ps || true
      docker compose -f "${COMPOSE_FILE}" logs --tail=200 "${svc}" 2>&1 || true
      exit 1
    fi

    echo "  ⏳ Status: ${status}"
    sleep 2
  done
done

echo "✓ All dependencies are healthy"
