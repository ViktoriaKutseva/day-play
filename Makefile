.PHONY: install test test-unit test-integration test-e2e lint format type-check security run config-check build-css help

help:
	@echo "Day-Play Development Commands"
	@echo "============================="
	@echo "make install         - Install dependencies with uv"
	@echo "make test            - Run all tests"
	@echo "make test-unit       - Run unit tests only"
	@echo "make test-integration - Run integration tests only"
	@echo "make test-e2e        - Run end-to-end tests"
	@echo "make lint            - Check code with ruff"
	@echo "make format          - Format code with ruff"
	@echo "make type-check      - Run mypy type checking"
	@echo "make build-css       - Build Tailwind CSS"
	@echo "make run             - Run development server"
	@echo "make all             - Run full CI pipeline locally"

install:
	uv sync

test: test-unit test-integration

test-unit:
	uv run pytest src/tests/unit/ -v --cov=src/day_play/models --cov=src/day_play/business

test-integration:
	uv run pytest src/tests/integration/ -v --cov=src/day_play/integrations

test-e2e:
	uv run pytest src/tests/e2e/ -v --cov=src/day_play/entrypoints

lint:
	uv run ruff check src

format:
	uv run ruff format src

type-check:
	uv run mypy src

security:
	uv run bandit -r src/
	uv tool install safety && uv run safety check

config-check:
	@echo "Validating configuration for all environments..."
	@ENVIRONMENT=development uv run python -c "from day_play.config.settings import settings; print(f'✓ Development config valid: {settings.app_name}')"
	@ENVIRONMENT=testing uv run python -c "from day_play.config.settings import settings; print(f'✓ Testing config valid: {settings.app_name}')"
	@echo "⚠ Production config requires DATABASE_URL env var - skipping validation"

build-css:
	npx @tailwindcss/cli --input src/day_play/entrypoints/web/static/css/main.css --output /tmp/main.css && cp /tmp/main.css src/day_play/entrypoints/web/static/css/main.css

run:
	uv run uvicorn day_play.entrypoints.api.main:app --reload --port 8001

all: format lint type-check config-check test security