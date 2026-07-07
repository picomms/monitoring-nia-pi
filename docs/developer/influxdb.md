# InfluxDB

InfluxDB 2.x is the single source of truth for all metrics. It's seeded automatically on first boot using Compose's `DOCKER_INFLUXDB_INIT_MODE: setup`.

## Initialization

On first start, `compose.yml` passes these environment variables to trigger InfluxDB's setup mode:

| Variable | Effect |
|---|---|
| `INFLUXDB_USER` / `INFLUXDB_PASSWORD` | Creates the initial admin user |
| `INFLUXDB_ADMIN_TOKEN` | Sets a fixed admin API token (rather than letting InfluxDB generate one) |
| `INFLUXDB_ORG` | Creates the initial organization |
| `INFLUXDB_BUCKET` | Creates the initial bucket |

Setup only runs once — if you change these values after the volumes already exist, InfluxDB will ignore them. Run `make clean` (destructive) or manually reconfigure via the InfluxDB UI/CLI to apply new org/bucket/token values to an existing instance.

## Who talks to InfluxDB

| Client | Auth | Org / Bucket used |
|---|---|---|
| Telegraf | `INFLUXDB_ADMIN_TOKEN` | `INFLUXDB_ORG` / `INFLUXDB_BUCKET` (from `.env`) |
| Grafana | `INFLUXDB_ADMIN_TOKEN` | Hardcoded `nia` / `nia` in `grafana/datasources/influxdb.yml` |
| `scripts/vimeo-exporter.py` | `INFLUX_ADMIN_TOKEN` (note the different variable name) | `INFLUX_ORG` / `INFLUX_BUCKET`, defaulting to `default` |

These three clients need to agree on the same org and bucket to see each other's data, and currently they don't by default — see the [Roadmap](../roadmap.md) for the specific mismatches and how to align them.

## Conventions

- One bucket for the whole stack; measurements (not buckets) separate concerns (see the data model table in [Architecture](architecture.md)).
- Prefer Flux over InfluxQL in new Grafana panels, matching the existing datasource configuration (`version: Flux`).
- Tag sparingly — most measurements here rely on the measurement name itself (`WP1`, `SpeedTest`, etc.) rather than tags to distinguish series, except `stream`, which tags by `device`.

## Accessing InfluxDB directly

The InfluxDB UI is available at `http://localhost:${INFLUXDB_PORT}` (default `8086`). Log in with `INFLUXDB_USER` / `INFLUXDB_PASSWORD`, or use the CLI from inside the container:

```bash
make exec SERVICE=influxdb2 CMD="influx query 'from(bucket:\"default\") |> range(start:-5m)'"
```
