# Configuration

All runtime configuration is driven by a `.env` file at the repo root (copy
`env.sample` to start). Docker Compose loads it automatically.

## Core

| Variable | Default | Description |
| --- | --- | --- |
| `TZ` | `Europe/Dublin` | Host timezone (informative; containers may still use UTC clocks) |
| `HOST_ID` | `cherry` | Short per-host slug used when creating monitoring hostnames |
| `PROMETHEUS_VERSION` | `v3.13.1` | `prom/prometheus` image tag |
| `GRAFANA_VERSION` | `13.0` | `grafana/grafana` image tag |
| `NODE_EXPORTER_VERSION` | `v1.12.0` | `quay.io/prometheus/node-exporter` image tag |
| `CLOUDFLARED_VERSION` | `2026.7.1` | `cloudflare/cloudflared` image tag |

## Ports

| Variable | Default | Description |
| --- | --- | --- |
| `PROMETHEUS_PORT` | `9090` | Host port for Prometheus UI / API |
| `GRAFANA_PORT` | `3000` | Host port for Grafana UI |

## Grafana

| Variable | Default | Description |
| --- | --- | --- |
| `GF_ADMIN_USER` | `admin` | Grafana admin username |
| `GF_ADMIN_PASSWORD` | `changeme` | Grafana admin password |
| `GRAFANA_HOST` | `localhost` | LAN fallback when `GRAFANA_ROOT_URL` is unset |
| `GRAFANA_ROOT_URL` | `https://mon-grafana.cothrom.ie` | Public Grafana URL behind Cloudflare Access |

## Cloudflare Tunnel (optional)

| Variable | Description |
| --- | --- |
| `TUNNEL_TOKEN` | Remotely managed tunnel token. Required only when starting with `just up-tunnel`. |

Hostname / Access setup is in [Cloudflare](../cloudflare.md). Compose only consumes
the token; ingress routes are managed in Zero Trust.
