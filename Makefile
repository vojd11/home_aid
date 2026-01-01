# Development commands
dev:
	docker-compose up -d

# Production commands
prod:
	docker-compose -f docker-compose.prod.yml up -d

# Stop all services
stop:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Database commands
db-migrate:
	docker-compose run --rm backend alembic upgrade head

db-rollback:
	docker-compose run --rm backend alembic downgrade -1

db-reset:
	docker-compose down -v
	docker-compose up -d postgres redis
	sleep 10
	docker-compose run --rm backend alembic upgrade head

# Backend commands
backend-shell:
	docker-compose exec backend bash

# Test commands
test:
	docker-compose run --rm backend python -m pytest tests/ -v

test-unit:
	docker-compose run --rm backend python -m pytest tests/unit/ -v

test-api:
	docker-compose run --rm backend python -m pytest tests/api/ -v

test-integration:
	docker-compose run --rm backend python -m pytest tests/integration/ -v

test-services:
	docker-compose run --rm backend python -m pytest tests/services/ -v

test-coverage:
	docker-compose run --rm backend python -m pytest tests/ --cov=app --cov-report=html --cov-report=term

backend-test: test

# Frontend commands
frontend-shell:
	docker-compose exec frontend bash

frontend-install:
	docker-compose run --rm frontend npm install

frontend-build:
	docker-compose run --rm frontend npm run build

# Cleanup
clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

.PHONY: dev prod stop logs db-migrate db-rollback db-reset backend-shell test test-unit test-api test-integration test-services test-coverage backend-test frontend-shell frontend-install frontend-build clean
