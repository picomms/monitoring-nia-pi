# Getting Started

## Prerequisites

- Docker and Docker Compose
- [just](https://github.com/casey/just)
- [uv](https://docs.astral.sh/uv/) (docs and Python scripts only)

## 1. Configure your environment

```bash
cp env.sample .env
```

Set at least `GF_ADMIN_USER` / `GF_ADMIN_PASSWORD`. See [Configuration](configuration.md)
for the full list.

## 2. Start the stack

```bash
just up
just ps
just logs
```

This starts Prometheus, Grafana, and `node_exporter`. Cloudflare Tunnel is **not**
started by default — use `just up-tunnel` once `TUNNEL_TOKEN` is set.

## 3. Open Grafana

Visit `http://localhost:${GRAFANA_PORT}` (default `3000`) and log in with the
credentials from `.env`. The **Cherry host** dashboard under **NIA Monitoring**
shows live CPU, memory, disk, and network metrics.

## 4. Verify data is flowing

1. Open Prometheus at `http://localhost:${PROMETHEUS_PORT}` (default `9090`) →
   **Status → Targets**. Both `prometheus` and `node` should be **UP**.
2. In Grafana, open **Cherry host** — panels should populate within a minute.

## Stopping

```bash
just down    # stop containers, keep NSD_* volumes
```

There is no one-shot volume wipe recipe. Remove orphaned volumes manually only if
you intend to discard TSDB / Grafana state.
