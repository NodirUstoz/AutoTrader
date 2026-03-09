.PHONY: help build up down logs migrate makemigrations superuser test lint shell flush collectstatic restart status

COMPOSE = docker compose
BACKEND = $(COMPOSE) exec backend
MANAGE  = $(BACKEND) python manage.py

help: ## Show this help message
	@echo "AutoTrader - Vehicle Marketplace Platform"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build all Docker images
	$(COMPOSE) build

up: ## Start all services in detached mode
	$(COMPOSE) up -d

down: ## Stop all services
	$(COMPOSE) down

restart: ## Restart all services
	$(COMPOSE) restart

status: ## Show status of all services
	$(COMPOSE) ps

logs: ## Tail logs from all services
	$(COMPOSE) logs -f

logs-backend: ## Tail logs from the backend service
	$(COMPOSE) logs -f backend

logs-celery: ## Tail logs from the celery worker
	$(COMPOSE) logs -f celery_worker

migrate: ## Run database migrations
	$(MANAGE) migrate --noinput

makemigrations: ## Generate new migration files
	$(MANAGE) makemigrations

superuser: ## Create a Django superuser
	$(MANAGE) createsuperuser

test: ## Run the backend test suite
	$(BACKEND) pytest -v --tb=short

test-cov: ## Run tests with coverage report
	$(BACKEND) pytest -v --cov=apps --cov-report=term-missing

lint: ## Run linters on backend code
	$(BACKEND) flake8 .
	$(BACKEND) isort --check-only .
	$(BACKEND) black --check .

format: ## Auto-format backend code
	$(BACKEND) isort .
	$(BACKEND) black .

shell: ## Open a Django shell
	$(MANAGE) shell_plus

dbshell: ## Open a database shell
	$(MANAGE) dbshell

flush: ## Flush the database (destructive)
	$(MANAGE) flush --noinput

collectstatic: ## Collect static files
	$(MANAGE) collectstatic --noinput

clean: ## Remove all containers, volumes, and images
	$(COMPOSE) down -v --rmi all --remove-orphans

frontend-shell: ## Open a shell in the frontend container
	$(COMPOSE) exec frontend sh

backend-shell: ## Open a bash shell in the backend container
	$(COMPOSE) exec backend bash

redis-cli: ## Open the Redis CLI
	$(COMPOSE) exec redis redis-cli

seed: ## Load seed data
	$(MANAGE) loaddata fixtures/*.json

dump: ## Dump current data to fixtures
	$(MANAGE) dumpdata accounts vehicles listings --indent 2 > backend/fixtures/data.json
