# Grafana

Grafana is fully provisioned from files in the repo — there is no manual dashboard setup step, and changes made through the Grafana UI will be overwritten on the next provisioning sync (every 30 seconds, per `updateIntervalSeconds`).

## Datasource

`grafana/datasources/influxdb.yml` provisions a single InfluxDB datasource:

```yaml
type: influxdb
access: proxy
url: http://influxdb2:8086
jsonData:
  version: Flux
  organization: nia
  defaultBucket: nia
secureJsonData:
  token: ${INFLUXDB_ADMIN_TOKEN}
```

The datasource uses Flux (not InfluxQL) and expects an organization/bucket named `nia`. This is hardcoded rather than templated from `INFLUXDB_ORG`/`INFLUXDB_BUCKET`, which default to `default` — see the [Roadmap](../roadmap.md) for aligning these.

## Dashboard provisioning

`grafana/dashboards/dashboards.yml` tells Grafana to load every dashboard JSON file in that directory into a folder called **NIA Stream**:

```yaml
providers:
  - name: NIA Stream Dashboards
    folder: NIA Stream
    type: file
    options:
      path: /etc/grafana/provisioning/dashboards
```

Both files are mounted read-only into the container via `compose.yml`.

## Editing a dashboard

Dashboards are plain JSON, hand-written rather than exported from the UI (there's no `__inputs` data and UIDs are stable, human-readable strings like `device-overview`). To make a change:

1. Edit the relevant file directly (e.g. `grafana/dashboards/general.json`).
2. Restart Grafana, or wait up to 30 seconds for the provisioning sync to pick it up: `make restart SERVICE=grafana`.
3. Refresh the dashboard in the browser.

Every panel targets the `influxdb_v2` datasource by UID and queries with Flux, e.g.:

```flux
from(bucket: v.defaultBucket)
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "WP1")
  |> filter(fn: (r) => r._field == "status")
  |> last()
```

Using `v.defaultBucket` (rather than hardcoding the bucket name) means dashboards keep working if the datasource's default bucket changes.

## Dashboard inventory

See [Dashboards](../user/dashboards.md) for a user-facing description of what each dashboard shows. From a maintenance perspective:

| File | UID | Template variables |
|---|---|---|
| `general.json` | `general` | none |
| `network-health.json` | `network-health` | none |
| `device-overview.json` | `device-overview` | none (hardcoded WP1–WP8 rows) |
| `device-page.json` | `device-page` | `$device` (custom, values `WP1`…`WP8`) |

Adding a ninth device means adding a new row to `device-overview.json` and a new option to the `$device` variable in `device-page.json` — there's no dynamic device discovery yet.
