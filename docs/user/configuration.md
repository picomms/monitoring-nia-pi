# Configuration

All configuration is driven by environment variables, loaded from a `.env` file at the repo root (copy `env.sample` to `.env` to start). Docker Compose reads `.env` automatically; Telegraf and the (future) FFmpeg service also read it via `env_file`.

!!! warning "Some variables used by configs are missing from `env.sample`"
    A few variables referenced by `telegraf.conf` and the Vimeo scripts are not yet templated in `env.sample`. They're documented below and tracked in the [Variable Review](../developer/variable-review.md) so `env.sample` can be brought fully in line.

## Core

| Variable | Default | Used by | Description |
|---|---|---|---|
| `TZ` | `Europe/Dublin` | telegraf, speedtest-tracker | Timezone for containers and displayed timestamps |
| `NETWORK_INTERFACE` | `["eth*", "enp0s[0-1]", "lo"]` | telegraf | Interface glob patterns for the `net` input plugin |
| `PUID` / `PGID` | `1000` | speedtest-tracker | User/group ID for file ownership inside the container |

## InfluxDB

| Variable | Default | Description |
|---|---|---|
| `INFLUXDB_VERSION` | `2` | Image tag for `influxdb` |
| `INFLUXDB_PORT` | `8086` | Host port mapped to InfluxDB's API |
| `INFLUXDB_USER` | `admin` | Initial admin username (setup mode only) |
| `INFLUXDB_PASSWORD` | `changeme` | Initial admin password (setup mode only) |
| `INFLUXDB_ADMIN_TOKEN` | `changeme` | API token used by Telegraf, Grafana, and the Vimeo scripts to write/read data |
| `INFLUXDB_ORG` | `default` | Organization created on first boot |
| `INFLUXDB_BUCKET` | `default` | Bucket created on first boot |

!!! warning "Org/bucket mismatch"
    `grafana/datasources/influxdb.yml` hardcodes organization and bucket `nia`, while these defaults are `default`. This is a deliberate workaround, not an oversight — Grafana's provisioning YAML doesn't reliably expand env vars for these particular fields. Set `INFLUXDB_ORG=nia` and `INFLUXDB_BUCKET=nia` in `.env` to match, or see the [Roadmap](../roadmap.md) for the full explanation.

## Grafana

| Variable | Default | Description |
|---|---|---|
| `GRAFANA_VERSION` | `13.0` | Image tag for `grafana/grafana` |
| `GRAFANA_PORT` | `3000` | Host port for the Grafana UI |
| `GF_ADMIN_USER` | `admin` | Grafana admin username |
| `GF_ADMIN_PASSWORD` | `changeme` | Grafana admin password |
| `GRAFANA_HOST` | `0.0.0.0` | Hostname used to build `GF_SERVER_ROOT_URL` |

## Speedtest Tracker

| Variable | Default | Description |
|---|---|---|
| `SPEEDTEST_TRACKER_PORT` | `8087` | Host port for the Speedtest Tracker UI |
| `SPEEDTEST_TRACKER_APP_KEY` | — | Laravel application encryption key required by Speedtest Tracker — internal to the app, not an API credential |
| `SPEEDTEST_TRACKER_HOST` | `localhost` | Hostname used to build `APP_URL`; set to your LAN IP for remote access |
| `SPEEDTEST_TRACKER_API_TOKEN` | — | A separate API token, generated in Speedtest Tracker's UI once it's running, for external consumers of its API |
| `SPEEDTEST_API_ACCESS_TOKEN` | — | **Not in `env.sample` yet.** This is the variable `telegraf.conf` actually reads to authenticate against the Speedtest Tracker API. It's likely meant to hold the same value as `SPEEDTEST_TRACKER_API_TOKEN` once generated, but the two are genuinely distinct tokens under the hood — see the [Variable Review](../developer/variable-review.md) before assuming they're interchangeable. |
| `ALLOWED_IPS` | unset (allow all) | Comma-separated list of client IPs allowed to access Speedtest Tracker |

## Web Presenter devices

Telegraf polls up to eight Blackmagic Web Presenter devices.

| Variable | Description |
|---|---|
| `STREAM1_HOST` … `STREAM8_HOST` | Hostname or IP of each Web Presenter, e.g. `192.168.1.101`. Telegraf queries `http://<host>/control/api/v1/livestreams/0` and `.../activePlatform` every 10 seconds. |

`env.sample` includes these commented out, with no example values — real device IPs are deliberately kept out of version control, since this repo runs a live deployment. Uncomment and fill in the ones you use in your own `.env`.

If you have fewer than eight devices, leave the unused `STREAM*_HOST` variables unset — the corresponding Grafana panels will simply show no data.

## Vimeo / FFmpeg (planned feature)

| Variable | Description |
|---|---|
| `VIMEO_TOKEN` | Vimeo API access token |
| `VIMEO_KEY` | Vimeo app client ID |
| `VIMEO_SECRET` | Vimeo app client secret |
| `VIMEO_EVENTID` | ID of the live event to probe |
| `DEVICE_NAME` | Tag applied to stream metrics published by `scripts/vimeo-exporter.py`, defaults to `encoder01` |
| `POLL_INTERVAL` | Seconds between probes in `ffmpeg/run.sh`, defaults to `60` |

See [FFmpeg / Vimeo](../developer/ffmpeg-vimeo.md) for how these fit together, and the [Roadmap](../roadmap.md) for why this service isn't enabled yet.
