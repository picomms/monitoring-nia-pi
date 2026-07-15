# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project summary

NIA Monitoring is the **server** Compose stack (project `monitoring-nia`) for
live-streaming infrastructure. Prometheus scrapes metrics; Grafana renders
provisioned PromQL dashboards. Primary deploy host is **Cherry**. Endpoint
exporters live in a separate repo (`docker-slice-pi`) — not here.

Architecture summary: `docs/developer/architecture.md` and
`docs/developer/decisions.md`. Prometheus operations:
`docs/developer/prometheus.md`. Docs publish to GitHub Pages (see
`.github/workflows/docs.yml`). Vimeo HLS / ffprobe exporter work lives in the
sibling `exporter-vimeo` repository.

## Repo map

| Path | What it is |
| --- | --- |
| `compose.yml` | Server stack (Prometheus, Grafana, node_exporter, optional cloudflared) |
| `justfile` | Common workflows — run `just --list` before raw `docker compose` / `uv` |
| `env.sample` | Template for `.env` |
| `prometheus/` | Prometheus scrape config; operational notes in `docs/developer/prometheus.md` |
| `grafana/` | Provisioned datasource + dashboard JSON (source of truth) |
| `docs/` | MkDocs source; `developer/decisions.md` is the concise architecture digest |
| `template/endpoint/` | Canonical RPi endpoint template (node, blackbox, speedtest; promote to `docker-slice-pi`) |
| `scripts/` | Operational helper scripts |
| `pyproject.toml` | Python deps for scripts + docs toolchain (`uv`) |

## Common commands

```bash
just up             # start Prometheus, Grafana, node_exporter
just up-tunnel      # also start cloudflared for Grafana (needs TUNNEL_TOKEN)
just prom-reload    # POST /-/reload after scrape config changes
just logs           # follow logs
just config         # print resolved compose config
just sync           # uv sync --all-extras
just docs-serve     # preview docs at :8000
just docs-build     # strict docs build (CI)
```

## Conventions

- Environment variables live in `.env` (gitignored), templated from `env.sample`.
  Never commit `.env` or real secrets. Remote scrapes use Tailscale MagicDNS
  targets in `prometheus/targets/`; Grafana uses Cloudflare Access.
- Docker volumes are prefixed `NSD_` — don't introduce unprefixed volumes.
- Compose networks: `frontend` (tunnel edge) and `backend` (internal). Do not pin
  bare external network names that collide with other stacks on the host.
- Grafana dashboards are edited as JSON in `grafana/dashboards/`, not only via the
  UI. Use stable, human-readable `uid` values.
- PromQL for new dashboards.
- Pin image tags in Compose / `env.sample`; avoid floating `:latest` for production.

## Known pitfalls

- `node_exporter` uses `pid: host` + rootfs bind on the `backend` network;
  Prometheus scrapes `node_exporter:9100` by Compose DNS (host-network hairpin
  to `host.docker.internal` is unreliable on this host).
- `cloudflared` is behind Compose profile `tunnel` — default `just up` will not
  start it.
- Alerting is a later epic; do not add Alertmanager/rules casually while doing
  routine stack maintenance.
- Do not put the NIA monitoring stack into `docker-cherry-pi` — that repo is for
  host-unique Cherry services only.

## Scope guidance for agents

- Documentation changes (README, `docs/`, `AGENTS.md`) can be made freely.
- Compose / Prometheus / Grafana / env changes are feature work — check the
  relevant docs and keep them in sync.
- When touching `compose.yml`, `prometheus/prometheus.yml`, Grafana provisioning,
  or `env.sample`, check the others for consistency.

## Do not

- Force-push to `main`.
- Commit `.env` or any file containing real tokens/credentials.
- Add a casual volume-wipe recipe — deleting `NSD_*` volumes destroys metric history.
