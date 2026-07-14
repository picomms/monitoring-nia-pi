# Configuration

All runtime configuration is driven by a `.env` file at the repo root (copy
`env.sample` to start). Docker Compose loads it automatically.

## Core

| Variable | Default | Description |
| --- | --- | --- |
| `TZ` | `Europe/Dublin` | Host timezone (informative; containers may still use UTC clocks) |
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
| `GRAFANA_HOST` | `localhost` | Hostname used to build `GF_SERVER_ROOT_URL` |

## Cloudflare Tunnel (optional)

| Variable | Description |
| --- | --- |
| `TUNNEL_TOKEN` | Remotely managed tunnel token. Required only when starting with `just up-tunnel`. |

Hostname / Access setup is documented later (milestone M2). Compose only consumes
the token.

## Vimeo / ffprobe (later — G2)

Not used by the M1 Compose stack. Commented placeholders remain in `env.sample`:

| Variable | Description |
| --- | --- |
| `VIMEO_TOKEN` | Access token |
| `VIMEO_KEY` | App client ID |
| `VIMEO_SECRET` | App client secret |
| `VIMEO_EVENTID` | Live event ID |
| `DEVICE_NAME` | Future metric label / instance name |

See [FFmpeg / Vimeo](../developer/ffmpeg-vimeo.md) for the working auth pattern and
API examples.
