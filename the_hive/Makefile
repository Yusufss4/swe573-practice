.PHONY: help install dev test run clean docker-build docker-up docker-down migrate

help:
	@echo "🐝 The Hive - Available Commands"
	@echo "================================"
	@echo "install      - Install dependencies"
	@echo "dev          - Install dev dependencies"
	@echo "test         - Run tests"
	@echo "test-cov     - Run tests with coverage"
	@echo "run          - Run development server"
	@echo "clean        - Clean cache and build files"
	@echo "docker-build - Build Docker image"
	@echo "docker-up    - Start Docker containers"
	@echo "docker-down  - Stop Docker containers"
	@echo "migrate      - Run database migrations"
	@echo "lint         - Run linters"
	@echo "format       - Format code"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	PYTHONPATH=. pytest tests/ -v

test-cov:
	PYTHONPATH=. pytest tests/ --cov=app --cov-report=html --cov-report=term

run:
	uvicorn app.main:app --reload

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov dist build

docker-build:
	docker build -t the_hive:latest -f infra/Dockerfile .

docker-up:
	cd infra && docker-compose up -d

docker-down:
	cd infra && docker-compose down

docker-logs:
	cd infra && docker-compose logs -f

migrate:
	alembic upgrade head

lint:
	ruff check app tests

format:
	black app tests
	ruff check --fix app tests
