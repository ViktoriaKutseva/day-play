.PHONY: install test test-unit test-integration test-e2e lint format type-check security run dev clean

# Project setup
install:
	uv sync

# Testing
test: test-unit test-integration test-e2e

test-unit:
	uv run pytest tests/unit/ --cov=src/day_play/models --cov=src/day_play/business

test-integration:
	uv run pytest tests/integration/ --cov=src/day_play/integrations

test-e2e:
	uv run pytest tests/e2e/ --cov=src/day_play/entrypoints

# Code quality
lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests

type-check:
	uv run mypy src

# Security
security:
	uv run pip-audit

# Running the application
run:
	uv run uvicorn src.day_play.entrypoints.api.main:app --reload

dev: install
	uv run uvicorn src.day_play.entrypoints.api.main:app --reload --port 8000

# Utilities
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/

# Complete check
all: format lint type-check test security