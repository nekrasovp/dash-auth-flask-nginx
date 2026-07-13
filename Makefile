.DEFAULT_GOAL := help

PYTHON ?= python3.13
VENV ?= .venv
APP_DIR := dash-auth-flask
VENV_PYTHON := $(abspath $(VENV))/bin/python
COMPOSE_DEV := docker compose -f docker-compose.yml -f docker-compose-development.yml

.PHONY: help setup install lint format test test-browser compose-config check up dev down logs seed clean-data

help: ## Show available commands
	@awk 'BEGIN {FS = ":.*## "; printf "Usage: make <target>\n\n"} /^[a-zA-Z_-]+:.*## / {printf "  %-16s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Create .env if needed and install development dependencies
	@test -f .env || cp .env.example .env
	@$(MAKE) install

$(VENV_PYTHON):
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install --upgrade pip

install: $(VENV_PYTHON) ## Install development dependencies
	$(VENV_PYTHON) -m pip install -r $(APP_DIR)/requirements-dev.txt

lint: ## Run Ruff lint and formatting checks
	cd $(APP_DIR) && $(VENV_PYTHON) -m ruff check .
	cd $(APP_DIR) && $(VENV_PYTHON) -m ruff format --check .

format: ## Apply Ruff formatting and safe lint fixes
	cd $(APP_DIR) && $(VENV_PYTHON) -m ruff check --fix .
	cd $(APP_DIR) && $(VENV_PYTHON) -m ruff format .

test: ## Run the non-browser test suite
	cd $(APP_DIR) && $(VENV_PYTHON) -m pytest -m "not browser"

test-browser: ## Run the Dash browser smoke test (requires Chrome/Chromium)
	cd $(APP_DIR) && $(VENV_PYTHON) -m pytest -m browser

compose-config: ## Validate production and development Compose models
	docker compose config --quiet
	$(COMPOSE_DEV) config --quiet

check: lint test compose-config ## Run the standard pull-request checks

up: ## Build and start the production-like stack
	docker compose up -d --build

dev: ## Start the hot-reload development stack
	$(COMPOSE_DEV) up --build

down: ## Stop containers while preserving SQLite data
	docker compose down

logs: ## Follow application and proxy logs
	docker compose logs -f app nginx

seed: ## Create the opt-in local demo user
	docker compose run --rm -e SEED_DEMO_USER=true app flask --app app:server seed-demo

clean-data: ## Stop containers and delete the local SQLite volume
	docker compose down --volumes
