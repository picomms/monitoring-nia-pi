# =============================================================================
# Stream Dashboard Makefile
# =============================================================================

SHELL := /bin/sh
.ONESHELL:
.SHELLFLAGS := -e -u -o pipefail -c

.DEFAULT_GOAL := help

.PHONY: help

COMPOSE ?= docker compose
SERVICE ?=
ARGS ?=
CMD ?= /bin/sh

help: ## Show this help message
	@echo "Stream Dashboard — common targets:"
	@fgrep -h "##" $(MAKEFILE_LIST) | grep -v fgrep | sed -e 's/\([^:]*\):[^#]*##\(.*\)/  \1|\2/' | column -t -s '|'

# -----------------------------------------------------------------------------
# Environment
# -----------------------------------------------------------------------------

install: ## Install uv (https://docs.astral.sh/uv/)
	curl -LsSf https://astral.sh/uv/install.sh | sh

sync: ## Install runtime + dev + docs dependencies
	uv sync --all-extras

# -----------------------------------------------------------------------------
# Documentation
# -----------------------------------------------------------------------------

.PHONY: docs-serve docs-build docs-deploy

docs-serve: ## Serve the docs locally with live reload (http://localhost:8000)
	uv run mkdocs serve

docs-build: ## Build the static docs site (fails on warnings)
	uv run mkdocs build --strict

docs-deploy: ## Build and push the docs site to the gh-pages branch
	uv run mkdocs gh-deploy --force

# -----------------------------------------------------------------------------
# Docker / Docker Compose
# -----------------------------------------------------------------------------

.PHONY: up down build rebuild restart logs ps exec sh pull config clean

up: ## Start the stack in the background (ARGS="--build" to rebuild)
	echo "[Docker Up]"
	$(COMPOSE) up -d $(ARGS) $(SERVICE)

down: ## Stop and remove containers, networks (ARGS="-v" to drop volumes)
	echo "[Docker Down]"
	$(COMPOSE) down $(ARGS)

build: ## Build (or rebuild) service images (SERVICE=name to target one)
	echo "[Docker Build]"
	$(COMPOSE) build $(ARGS) $(SERVICE)

rebuild: ## Build images without cache and recreate containers
	echo "[Docker Rebuild]"
	$(COMPOSE) build --no-cache $(SERVICE)
	$(COMPOSE) up -d --force-recreate $(SERVICE)

restart: ## Restart services (SERVICE=name to target one)
	echo "[Docker Restart]"
	$(COMPOSE) restart $(SERVICE)

logs: ## Follow logs (SERVICE=name to target one)
	$(COMPOSE) logs -f --tail=100 $(SERVICE)

ps: ## List running containers
	echo "[Docker PS]"
	$(COMPOSE) ps

config: ## Validate and render the resolved compose configuration
	echo "[Docker Config]"
	$(COMPOSE) config

pull: ## Pull the latest images for all services
	echo "[Docker Pull]"
	$(COMPOSE) pull $(SERVICE)

exec: ## Run a command in a service (SERVICE=name CMD="...", defaults to shell)
	@test -n "$(SERVICE)" || { echo "SERVICE is required, e.g. make exec SERVICE=grafana"; exit 1; }
	echo "[Docker Exec]"
	$(COMPOSE) exec $(SERVICE) $(CMD)

sh: ## Open an interactive shell in a service (SERVICE=name)
	@test -n "$(SERVICE)" || { echo "SERVICE is required, e.g. make sh SERVICE=grafana"; exit 1; }
	echo "[Docker Shell]"
	$(COMPOSE) exec $(SERVICE) /bin/sh

clean: ## Stop stack, remove NSD_* volumes, and prune unused Docker resources
	$(MAKE) down
	@echo "[Clean] Removing NSD_* volumes..."
	@for vol in $$(docker volume ls -q --filter name=NSD_); do \
		if [ -n "$$vol" ]; then \
			echo "  Removing volume $$vol"; \
			docker volume rm "$$vol" || true; \
		fi; \
	done
	@echo "[Clean] Pruning stopped containers, unused networks, and dangling images..."
	@docker system prune -f

# -----------------------------------------------------------------------------
# Scripts
# -----------------------------------------------------------------------------

.PHONY: script

SCRIPT ?= vimeoprobe.py

script: ## Run a script (SCRIPT=name.py, default vimeodata.py)
	$(COMPOSE) run --rm --entrypoint python ffmpeg scripts/$(SCRIPT)
