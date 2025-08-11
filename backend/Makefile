.PHONY: help install dev test lint format clean docker-build docker-up docker-down migrate

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Run development server"
	@echo "  worker      - Run Celery worker"
	@echo "  beat        - Run Celery beat scheduler"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo "  clean       - Clean up generated files"
	@echo "  docker-build - Build Docker images"
	@echo "  docker-up   - Start Docker services"
	@echo "  docker-down - Stop Docker services"
	@echo "  migrate     - Run database migrations"

# Install dependencies
install:
	pip install -r requirements.txt
	pip install -e ".[dev]"

# Development server
dev:
	python run_dev.py

# Celery worker
worker:
	python run_worker.py

# Celery beat
beat:
	python run_beat.py

# Run tests
test:
	pytest

# Run tests with coverage
test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

# Lint code
lint:
	flake8 app/
	mypy app/

# Format code
format:
	black app/ tests/
	isort app/ tests/

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Database migrations
migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(MSG)"

migrate-rollback:
	alembic downgrade -1

# Setup development environment
setup-dev:
	cp .env.example .env
	mkdir -p uploads generated templates logs
	pip install -r requirements.txt
	pip install -e ".[dev]"
	@echo "Development environment setup complete!"
	@echo "1. Edit .env file with your configuration"
	@echo "2. Set up PostgreSQL database"
	@echo "3. Run 'make migrate' to apply database migrations"
	@echo "4. Run 'make dev' to start the development server"

# Production deployment
deploy:
	docker-compose -f docker-compose.yml up -d
	docker-compose exec api alembic upgrade head

# Health check
health:
	curl -f http://localhost:8000/health || exit 1

# Monitor services
monitor:
	docker-compose ps
	docker-compose logs --tail=50 api worker beat

# Backup database
backup-db:
	docker-compose exec db pg_dump -U user lazulite_ppt > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Restore database
restore-db:
	@echo "Usage: make restore-db FILE=backup_file.sql"
	docker-compose exec -T db psql -U user lazulite_ppt < $(FILE)

# Security scan
security:
	pip install safety bandit
	safety check
	bandit -r app/

# Performance test
perf-test:
	pip install locust
	locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Generate API documentation
docs:
	pip install sphinx sphinx-rtd-theme
	sphinx-build -b html docs/ docs/_build/

# Update dependencies
update-deps:
	pip-compile requirements.in
	pip-compile requirements-dev.in

# Check code quality
quality:
	pip install radon
	radon cc app/ -a
	radon mi app/
	radon raw app/

# Run all checks
check-all: lint test security quality
	@echo "All checks completed!"