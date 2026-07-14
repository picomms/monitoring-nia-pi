# NIA Monitoring endpoint stack — common ops recipes
# Source of truth docs: https://picomms.github.io/monitoring-nia-pi/

set dotenv-load := false
set shell := ["bash", "-euo", "pipefail", "-c"]

default: help

help:
    @just --list

# Start cloudflared, node_exporter, blackbox_exporter
up:
    docker compose up -d

# Stop containers
down:
    docker compose down

# Show running containers
ps:
    docker compose ps

# Follow logs (optional: just logs cloudflared)
logs *SERVICE:
    docker compose logs -f {{SERVICE}}

# Print resolved Compose config
config:
    docker compose config
