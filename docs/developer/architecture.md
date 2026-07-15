# Architecture

Everything is defined in `compose.yml` under the Compose project name
`monitoring-nia`. The [Decisions](decisions.md) page summarizes the locked
architecture; the complete record lives in `refactor.md` at the repo root.

## Services (M1)

```mermaid
flowchart TB
  subgraph backend [backend network]
    Prometheus[prometheus]
    Grafana[grafana]
    NE[node_exporter]
  end
  subgraph frontend [frontend network]
    Grafana
    CF["cloudflared\n(profile: tunnel)"]
  end
  NE -->|node_exporter:9100| Prometheus
  Grafana --> Prometheus
  CF -.-> Grafana
```

| Service | Image | Networks | Notes |
| --- | --- | --- | --- |
| `prometheus` | `prom/prometheus` | backend | Scrapes self + Cherry `node_exporter`; TSDB on `NSD_prometheus_data` |
| `grafana` | `grafana/grafana` | backend, frontend | Provisioned datasource + dashboards; LAN port published |
| `node_exporter` | `quay.io/prometheus/node-exporter` | backend | `pid: host` + rootfs bind; scraped as `node_exporter:9100` |
| `cloudflared` | `cloudflare/cloudflared` | frontend | Profile `tunnel` only; needs `TUNNEL_TOKEN` |

Legacy `telegraf/` and future-G2 `ffmpeg/` / `scripts/` directories remain on
disk but are **not** started by Compose.

## Networks

| Network | Purpose |
| --- | --- |
| `backend` | Internal stack traffic (Prometheus ↔ Grafana) |
| `frontend` | Tunnel-facing edge (`cloudflared`, Grafana dual-homed) |

Networks are project-scoped (not shared bare `frontend`/`backend` names) so this
stack does not collide with other Compose projects on Cherry.

## Volumes

| Volume | Contents |
| --- | --- |
| `NSD_prometheus_data` | Prometheus TSDB |
| `NSD_grafana_data` | Grafana internal DB |

## Data model

Prometheus metrics with labels. Scrape jobs today:

| Job | Target | Purpose |
| --- | --- | --- |
| `prometheus` | `localhost:9090` | Self-metrics |
| `node` | `node_exporter:9100` | Cherry host (`instance=cherry`) |
| `node_remote` | `*.taild08b87.ts.net:9100` | Slice hosts over Tailscale |
| `blackbox` | `*.taild08b87.ts.net:9115` | Blackbox exporter metrics |
| `probe_icmp` | blackbox `/probe` | ICMP via each slice |

See [Prometheus](prometheus.md) for file SD, Access headers, health checks, and
reload. Alertmanager arrives in M5.

Endpoint Pis run a separate Compose template (`cloudflared` + `node_exporter` +
`blackbox_exporter`). See [Slice](slice.md).
