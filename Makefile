.PHONY: help run test lint build clean dev

help:
@echo "TaskQuest Academy - Development Commands"
@echo ""
@echo "Usage:"
@echo "  make run       - Start all services with Docker Compose"
@echo "  make dev       - Start API in development mode (without Docker)"
@echo "  make test      - Run API tests"
@echo "  make lint      - Run linting (ruff + mypy)"
@echo "  make build     - Build Docker images"
@echo "  make clean     - Remove containers and volumes"
@echo ""

run:
docker compose up --build

dev:
cd services/api && uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
cd services/api && pytest tests/ -v --cov=. --cov-report=term-missing

lint:
ruff check services/api/
mypy services/api/main.py --ignore-missing-imports

build:
docker compose build

clean:
docker compose down -v --remove-orphans
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name ".coverage" -delete 2>/dev/null || true
