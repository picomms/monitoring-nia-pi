# Variable Review

## Why this exists

While drafting the [roadmap](../roadmap.md), a few "env var mismatches" turned out not to be simple naming bugs at all — for example, the Speedtest Tracker app key and its API access token are two genuinely different values that just happen to look similar from the outside. Renaming things one at a time based on that kind of surface-level assumption is how you introduce new bugs. This page is a proper audit instead: every variable, what it's actually for, who reads it, and whether it's currently documented correctly.

This is a living working document, not a finished reference. Once it's confirmed accurate, fold the results into [Configuration](../user/configuration.md) and retire (or archive) this page.

## Scope

Every variable read by:

- `compose.yml`
- `telegraf/telegraf.conf`
- `grafana/datasources/influxdb.yml`
- `scripts/vimeo-exporter.py` and `scripts/vimeodata.py`
- `ffmpeg/run.sh`

## Audit table

| Variable | Consumer(s) | Purpose | In `env.sample`? | Notes |
|---|---|---|---|---|
| `TZ` | speedtest-tracker, telegraf | Container timezone | Yes | |
| `NETWORK_INTERFACE` | telegraf | Interface glob patterns for `inputs.net` | Yes | |
| `PUID` / `PGID` | speedtest-tracker | File ownership inside the container | Yes | |
| `INFLUXDB_PORT` | `compose.yml` | Host port for InfluxDB | Yes | |
| `INFLUXDB_VERSION` | `compose.yml` | Image tag | Yes | |
| `INFLUXDB_USER` / `INFLUXDB_PASSWORD` | influxdb2 (setup mode only) | Initial admin credentials | Yes | Only applied the first time the volume is created |
| `INFLUXDB_ADMIN_TOKEN` | influxdb2, telegraf, grafana | API token for read/write access | Yes | |
| `INFLUXDB_ORG` / `INFLUXDB_BUCKET` | influxdb2, telegraf | Org/bucket created on first boot | Yes | Default `default`/`default`; Grafana's datasource hardcodes `nia`/`nia` instead of reading these — see the [roadmap](../roadmap.md) |
| `GRAFANA_VERSION` | `compose.yml` | Image tag | Yes | |
| `GRAFANA_PORT` | `compose.yml` | Host port | Yes | |
| `GF_ADMIN_USER` / `GF_ADMIN_PASSWORD` | grafana | Admin login | Yes | |
| `GRAFANA_HOST` | grafana | Used to build `GF_SERVER_ROOT_URL` | Yes | |
| `SPEEDTEST_TRACKER_PORT` | `compose.yml` | Host port | Yes | |
| `SPEEDTEST_TRACKER_APP_KEY` | speedtest-tracker | Laravel application encryption key — internal to the app, not an API credential | Yes | |
| `SPEEDTEST_TRACKER_HOST` | speedtest-tracker | Used to build `APP_URL` | Yes | |
| `SPEEDTEST_TRACKER_API_TOKEN` | *(documented, not currently wired into any config)* | API token generated inside Speedtest Tracker's UI after it's running, for external consumers of its API | Yes | Confirmed to be a genuinely separate value from `SPEEDTEST_TRACKER_APP_KEY` |
| `SPEEDTEST_API_ACCESS_TOKEN` | telegraf | Bearer token Telegraf sends when polling the Speedtest Tracker results API | **No** | Likely meant to hold the same value as `SPEEDTEST_TRACKER_API_TOKEN` once generated — needs confirming, see [Next steps](#next-steps) |
| `ALLOWED_IPS` | speedtest-tracker | Optional comma-separated IP allowlist | Yes (commented out) | |
| `VIMEO_TOKEN` / `VIMEO_KEY` / `VIMEO_SECRET` | `scripts/vimeodata.py`, `scripts/vimeo-exporter.py` | Vimeo API credentials | Yes | |
| `VIMEO_EVENTID` | `scripts/vimeodata.py`, `scripts/vimeo-exporter.py` | Live event ID to probe | Yes | |
| `DEVICE_NAME` | `scripts/vimeo-exporter.py` | Tag applied to `stream` measurement points | Yes | |
| `POLL_INTERVAL` | `ffmpeg/run.sh` | Seconds between probes (default `60`) | **No** | |
| `STREAM1_HOST` … `STREAM8_HOST` | telegraf | Web Presenter device hosts | Placeholder only (commented out) | Real values intentionally excluded from version control — see the [roadmap](../roadmap.md) |
| `INFLUX_URL` / `INFLUX_ADMIN_TOKEN` / `INFLUX_ORG` / `INFLUX_BUCKET` | `scripts/vimeo-exporter.py` | Should be the same InfluxDB connection everything else uses | **No — wrong prefix** | Needs renaming to the `INFLUXDB_*` convention as part of building out the exporter (see [FFmpeg / Vimeo](ffmpeg-vimeo.md)) |

## Next steps

1. Confirm whether `SPEEDTEST_TRACKER_API_TOKEN` and `SPEEDTEST_API_ACCESS_TOKEN` are meant to hold the same value once Speedtest Tracker's API token is generated. If so, either alias them in `telegraf.conf` or document clearly that both must be set to the same secret; if not, document what actually distinguishes them.
2. Add `POLL_INTERVAL` to `env.sample` with a sensible documented default.
3. As the Vimeo exporter gets built out, rename its `INFLUX_*` variables to `INFLUXDB_*` for consistency with the rest of the stack.
4. Decide whether `INFLUXDB_ORG`/`INFLUXDB_BUCKET` defaults should change to `nia` to match Grafana's hardcoded datasource values, or whether Grafana's provisioning should instead be made to read the real env vars (revisit if a future Grafana version changes how provisioning files expand env vars).
5. Once every row above is confirmed accurate, merge the final version into [Configuration](../user/configuration.md) and mark this page as archived.
