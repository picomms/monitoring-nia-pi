# Prometheus

Prometheus is the metrics store and scraper for the server stack. Its
configuration is versioned in `prometheus/prometheus.yml` and mounted read-only
into the container.

## Local scrape jobs

| Job | Target | Labels | Purpose |
| --- | --- | --- | --- |
| `prometheus` | `localhost:9090` | default | Prometheus self-metrics |
| `node` | `node_exporter:9100` | `instance=cherry` | Cherry host metrics |

The server also sets `external_labels.monitor: cherry`, which will distinguish
this Prometheus instance when the Apple mirror is added later.

## Why the node target uses Compose DNS

`node_exporter` runs with `pid: host` and a read-only root filesystem bind so it
can report real host CPU, memory, disk, process, and filesystem metrics. It still
joins the Compose `backend` network, allowing Prometheus to scrape it by service
name at `node_exporter:9100`.

M1 initially tested a host-networked exporter through
`host.docker.internal:9100`. Docker hairpin traffic timed out on Cherry because
of its iptables path. Keeping the exporter on `backend` avoids that dependency
while preserving the host visibility required by the collectors.

## Health checks

Prometheus health endpoint:

```bash
curl --fail http://localhost:9090/-/healthy
```

Open **Status → Targets** in the Prometheus UI and confirm both local jobs are
**UP**. To query the node scrape directly:

```bash
curl --get http://localhost:9090/api/v1/query \
  --data-urlencode 'query=up{job="node"}'
```

The result should contain a sample with value `1`.

## Applying configuration changes

Validate the resolved Compose model first:

```bash
just config
```

Prometheus starts with `--web.enable-lifecycle`, so a valid scrape-config change
can be reloaded without restarting the container:

```bash
curl --request POST http://localhost:9090/-/reload
```

If the reload fails, inspect `just logs prometheus`. Recreating the service is a
safe fallback:

```bash
docker compose up -d --force-recreate prometheus
```

No rule files or Alertmanager configuration are loaded yet; those belong to M5.
