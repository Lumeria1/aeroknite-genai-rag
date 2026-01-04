# =============================================================================
# AEROKNITE GENAI RAG - MAKEFILE
# =============================================================================
# CI-safe: No venv activation needed (uses explicit tool paths)
# Windows + WSL2 compatible
# =============================================================================

SHELL := /bin/bash
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
RUFF := $(VENV)/bin/ruff
BLACK := $(VENV)/bin/black
MYPY := $(VENV)/bin/mypy

.PHONY: help setup format lint typecheck test test-unit test-integration clean dev down logs ps

help:
	@echo "========================================="
	@echo "Aeroknite GenAI RAG - Available Commands"
	@echo "========================================="
	@echo "Setup:"
	@echo "  make setup            - Create .venv + install dev tools"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format           - Auto-format (black + ruff --fix)"
	@echo "  make lint             - Check formatting + linting"
	@echo "  make typecheck        - Run mypy type checks"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            - Remove caches/artifacts"

setup:
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV)
	@echo "Upgrading pip..."
	$(PYTHON) -m pip install -U pip
	@echo "Installing dev tools..."
	$(PIP) install ruff black mypy pytest pytest-cov
	@echo "✓ Setup complete"

format:
	@echo "Running black formatter..."
	$(BLACK) .
	@echo "Running ruff auto-fixes..."
	$(RUFF) check . --fix
	@echo "✓ Formatting complete"

lint:
	@echo "Running ruff..."
	$(RUFF) check .
	@echo "Running black check..."
	$(BLACK) --check .
	@echo "✓ Lint checks passed"

typecheck:
	@echo "Running mypy..."
	$(MYPY) services libs
	@echo "✓ Type checks passed"

test:
	@echo "Running tests..."
	$(PYTEST)

test-unit:
	@echo "Running unit tests..."
	$(PYTEST) -m unit

test-integration:
	@echo "Running integration tests..."
	RUN_INTEGRATION=1 $(PYTEST) -m integration

clean:
	@echo "Cleaning caches..."
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Clean complete"

dev:
	@echo "Checking environment configuration..."
	@if [ ! -f .env ]; then \
		echo "⚠️  .env not found. Creating from .env.example..."; \
		cp .env.example .env; \
		echo ""; \
		echo "📝 IMPORTANT: Edit .env with real credentials before Stage 3+."; \
		echo "Press Ctrl+C to abort, or wait 5 seconds to continue..."; \
		sleep 5; \
	fi
	@echo "Starting local stack (infra/docker-compose.yml)..."
	docker compose -f infra/docker-compose.yml up -d --build
	@echo "✓ Stack started"
	@echo "Query Service: http://localhost:8000"
	@echo "Stack is running in the background. Use 'make down' to stop it."
	@echo "To view logs, use 'make logs'."
	@echo "To stop the stack, use 'make down'."
	@echo "To see running containers, use 'make ps'."

down:
	@echo "Stopping local stack..."
	docker compose -f infra/docker-compose.yml down -v
	@echo "✓ Stack stopped (volumes removed)"
	@echo "Local stack stopped. You can restart it with 'make dev'."

logs:
	@echo "Tailing logs..."
	docker compose -f infra/docker-compose.yml logs -f --tail=200
	@echo "✓ Logs streaming ended"
	@echo "Press Ctrl+C to stop viewing logs."
	@echo "Use 'make ps' to see running containers."
	@echo "Use 'make down' to stop the stack."

ps:
	docker compose -f infra/docker-compose.yml ps
	@echo "✓ Listed running containers"
	@echo "Use 'make logs' to view logs."
	@echo "Use 'make down' to stop the stack."
	@echo "Use 'make dev' to start the stack."
