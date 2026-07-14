# NIA Monitoring — common ops recipes
# https://github.com/casey/just

set dotenv-load := false
set shell := ["bash", "-euo", "pipefail", "-c"]

default: help

help:
    @just --list

# Start the stack (Prometheus, Grafana, node_exporter)
up:
    docker compose up -d

# Start the stack including cloudflared (requires TUNNEL_TOKEN in .env)
up-tunnel:
    docker compose --profile tunnel up -d

# Stop containers (keep volumes)
down:
    docker compose down

# Show running containers
ps:
    docker compose ps

# Follow logs (optional: just logs grafana)
logs *SERVICE:
    docker compose logs -f {{SERVICE}}

# Print resolved Compose config
config:
    docker compose config

# Install Python deps (scripts + docs)
sync:
    uv sync --all-extras

# Preview docs at http://localhost:8000
docs-serve: sync
    uv run mkdocs serve -a 0.0.0.0:8000

# Strict docs build (used in CI)
docs-build: sync
    uv run mkdocs build --strict
