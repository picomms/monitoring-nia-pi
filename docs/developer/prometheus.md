# Prometheus

Prometheus is the metrics store and scraper for the server stack. Its
configuration is versioned in `prometheus/prometheus.yml` and mounted read-only
into the container. Fleet targets live under `prometheus/targets/` (file SD).

## Scrape jobs

| Job | Targets | Labels | Purpose |
| --- | --- | --- | --- |
| `prometheus` | `localhost:9090` | default | Prometheus self-metrics |
| `node` | `node_exporter:9100` | `instance=cherry` | Cherry host metrics |
| `node_remote` | `<host>.taild08b87.ts.net:9100` | `instance=<HOST_ID>` | Slice host metrics (Tailscale) |
| `blackbox` | `<host>.taild08b87.ts.net:9115` | `instance=<HOST_ID>` | Blackbox exporter self-metrics |
| `probe_icmp` | each slice blackbox `/probe` | `instance=<HOST_ID>` | ICMP to `1.1.1.1` via that Pi |
| `speedtest` | `speedtest-tracker:80` | `instance=cherry` | Local Speedtest Tracker `/prometheus` |
| `speedtest_remote` | `<host>.taild08b87.ts.net:8765` | `instance=<HOST_ID>` | Slice Speedtest Tracker |

Current fleet: `streamrtn1`–`streamrtn4`. Add a host by editing
`prometheus/targets/*.yml` and running `just prom-reload`. Speedtest jobs use
`scrape_interval: 60s` and `metrics_path: /prometheus`.

Grafana for humans uses Cloudflare (`mon-grafana.cothrom.ie`); remote scrapes do
**not** use Cloudflare Access or `mon-node-*` hostnames.

The server sets `external_labels.monitor: cherry` for the future Apple mirror.

## Tailscale DNS from the container

Prometheus uses Tailscale MagicDNS resolver `100.100.100.100` (see `compose.yml`
`dns:`) so `*.ts.net` names resolve inside the container. The host must be on the
tailnet (`tailscale status`).

## Why the local node target uses Compose DNS

`node_exporter` runs with `pid: host` and a read-only root filesystem bind so it
can report real host CPU, memory, disk, process, and filesystem metrics. It still
joins the Compose `backend` network, allowing Prometheus to scrape it by service
name at `node_exporter:9100`.

## Health checks

```bash
curl --fail http://localhost:9090/-/healthy
```

Open **Status → Targets** and confirm local plus remote jobs are **UP**:

```bash
curl --get http://localhost:9090/api/v1/query \
  --data-urlencode 'query=up{job="node_remote"}'
curl --get http://localhost:9090/api/v1/query \
  --data-urlencode 'query=probe_success{job="probe_icmp"}'
```

## Applying configuration changes

```bash
just config
just prom-reload    # POST /-/reload (lifecycle enabled)
```

If reload fails, inspect `just logs prometheus` or recreate:

```bash
docker compose up -d --force-recreate prometheus
```

Grafana: provisioned **Fleet hosts** dashboard (`uid: fleet-hosts`).

No rule files or Alertmanager yet; alerting is a later epic.
