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

.PHONY: help setup format lint typecheck test test-unit test-integration clean

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
	$(PYTEST) -m integration

clean:
	@echo "Cleaning caches..."
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Clean complete"