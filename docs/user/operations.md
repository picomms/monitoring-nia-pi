# Operations

Day-to-day tasks. Prefer `just` recipes (`just --list` for the full set).

## Starting and stopping

```bash
just up          # Prometheus, Grafana, node_exporter
just up-tunnel   # also start cloudflared (needs TUNNEL_TOKEN)
just down        # stop containers; keep NSD_* volumes
```

## Logs and status

```bash
just logs              # follow all services
just logs grafana      # one service
just ps
just config            # resolved Compose config
```

## Checking metrics

```bash
curl --fail http://localhost:9090/-/healthy
```

In the Prometheus UI, open **Status → Targets**. Local jobs (`prometheus`,
`node`, `speedtest`) should be **UP**; remote jobs (`node_remote`, `blackbox`,
`probe_icmp`, `speedtest_remote`) should be **UP** when Tailscale and the slice
hosts are reachable. See [Prometheus](../developer/prometheus.md) for query
checks and troubleshooting.

After editing `prometheus/prometheus.yml`, apply a validated configuration:

```bash
just config
curl --request POST http://localhost:9090/-/reload
```

## Cloudflare profile

`just up` does not start `cloudflared`. Set `TUNNEL_TOKEN` and
`GRAFANA_ROOT_URL=https://mon-grafana.cothrom.ie` in `.env`, then run
`just up-tunnel` when the remotely managed tunnel is ready. The container has no
published host port; it reaches Grafana over the Compose `frontend` network.
See [Cloudflare](../cloudflare.md) for the `cothrom.ie` hostname and Access setup.

## Docs

```bash
just sync         # install Python deps via uv
just docs-serve   # http://localhost:8000
just docs-build   # mkdocs build --strict
```

## Volumes

Persistent state uses the `NSD_` prefix:

| Volume | Contents |
| --- | --- |
| `NSD_prometheus_data` | Prometheus TSDB |
| `NSD_grafana_data` | Grafana users / sessions (dashboards are provisioned from git) |
| `NSD_speedtest_tracker_data` | Speedtest Tracker app data |

There is no `just clean`. To discard monitoring history deliberately:

```bash
just down
docker volume rm monitoring-nia_NSD_prometheus_data monitoring-nia_NSD_grafana_data monitoring-nia_NSD_speedtest_tracker_data
```
