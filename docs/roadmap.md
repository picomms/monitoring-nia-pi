# Roadmap

The core monitoring stack (Telegraf, InfluxDB, Grafana, Speedtest Tracker) has reached MVP. This page is the honest, up-to-date account of what's still broken or unfinished, and what's being built next. Treat it as a living document — update it as issues are fixed or new ones are found.

## Priorities

In order:

1. **Stream health dashboard**, backed by a fully-built FFmpeg/Vimeo probe — the biggest visibility gap today. See [Planned work](#planned-work-ffmpeg-vimeo-stream-probe) and [FFmpeg / Vimeo](developer/ffmpeg-vimeo.md).
2. **Environment variable review** — several items below turned out to be more nuanced than a simple naming mismatch, so they're being tracked through a proper audit instead of one-off renames. See [Variable Review](developer/variable-review.md).
3. Everything else in the tables below, roughly top to bottom.

## Known issues

### Data connections / configuration

| Issue | Status | Details | Files |
|---|---|---|---|
| Grafana ↔ InfluxDB org/bucket mismatch | Known limitation, workaround in place | Grafana's datasource provisioning doesn't reliably expand `${...}` env vars for the `organization`/`defaultBucket` fields (only `secureJsonData.token` is confirmed to work), so these are hardcoded to `nia`/`nia` as a deliberate bypass. Set `INFLUXDB_ORG=nia` and `INFLUXDB_BUCKET=nia` in `.env` to match until a cleaner fix is found. | `grafana/datasources/influxdb.yml`, `env.sample` |
| Speedtest token naming | Not a bug — two distinct tokens | `SPEEDTEST_TRACKER_APP_KEY`/`SPEEDTEST_TRACKER_API_TOKEN` and the value `telegraf.conf` reads (`SPEEDTEST_API_ACCESS_TOKEN`) are genuinely different: one is Speedtest Tracker's own internal token, the other is a separate API access token generated after the app is up and running. The naming just isn't obvious from the outside. Tracked properly in the [variable review](developer/variable-review.md) rather than patched as a quick rename. | `telegraf/telegraf.conf`, `env.sample` |
| Web Presenter hosts | Intentional omission — placeholders added | `STREAM1_HOST`–`STREAM8_HOST` are real device IPs for a repo that's in "soft"/partial production use, so they were deliberately left out of `env.sample` rather than forgotten. Commented-out placeholder entries now document the expected shape without exposing real infrastructure. | `telegraf/telegraf.conf`, `env.sample` |
| Vimeo exporter | Scaffolding only — needs full development | `scripts/vimeo-exporter.py` (wrong `INFLUX_*` env var names, the missing `require_env` helper, etc.) was never a finished feature to begin with — it's scaffolding. Rather than patch it in isolation, it's being built out properly alongside the FFmpeg service. See [Planned work](#planned-work-ffmpeg-vimeo-stream-probe). | `scripts/vimeo-exporter.py` |
| Speedtest Tracker port fallback | **Fixed** | `compose.yml`'s fallback for `SPEEDTEST_TRACKER_PORT` now matches `env.sample`'s default of `8087` instead of falling back to `80`. | `compose.yml` |
| Speedtest `json_v2` drops whole metric mid-test | **Fixed** | When Speedtest Tracker is running a test, nested `data.data.*` paths briefly disappear; without `optional = true` on those fields, Telegraf aborted the entire `SpeedTest` measurement for that poll (including `download`, `upload`, `isp`, etc.). | `telegraf/telegraf.conf` |

### Dashboards

| Issue | Priority | Details |
|---|---|---|
| No stream health panels | **Top priority** | `vimeo-exporter.py` is designed to write a `stream` measurement, but no Grafana dashboard queries it yet. Blocked on finishing the FFmpeg/Vimeo probe below. |
| Device dashboards assume all 8 devices exist | Backlog, not urgent | `device-overview.json` and `device-page.json` hardcode WP1–WP8. Not causing problems for current deployments; a more dynamic, device-count-aware layout is a candidate future feature rather than something to fix now. |
| Web Presenter bitrate unit mismatch | **Fixed** | The Web Presenter API returns `bitrate` in bits/sec, but dashboards used `kbytes` (and a 0–10000 max), making values look like GB/s. Panels now convert to Mbps and use 0–15 fuel gauges. | `grafana/dashboards/device-overview.json`, `grafana/dashboards/device-page.json`, `grafana/dashboards/general.json` |
| Speedtest throughput scale wrong | **Fixed** | Speedtest Tracker's `download`/`upload` fields are Bytes/sec; dashboards divided by 1,000,000 and labelled Mbits, under-reporting by 8×. Queries now use `* 8.0 / 1000000.0`. | `grafana/dashboards/general.json`, `grafana/dashboards/network-health.json` |
| Device Page audio bitrate panel | **Fixed** | Web Presenter firmware does not expose an audio bitrate field; the panel was removed. Stream Duration over Time was replaced with a Status History timeline. | `grafana/dashboards/device-page.json` |
| String stat panels show "No data" | **Fixed** | Status and Active Platform are string fields; Stat panels used `color.mode: thresholds` and `lastNotNull`, which Grafana cannot render for strings. Panels now use `color.mode: value`, `type: string`, `last` reduction, and a field-name filter transformation. | `grafana/dashboards/device-overview.json`, `grafana/dashboards/device-page.json` |

### Infrastructure cleanup

| Issue | Status | Details |
|---|---|---|
| Unused volume | **Fixed** | `NSD_db_data` has been removed from `compose.yml` — it was declared but never mounted by any service. |

## Planned work: FFmpeg / Vimeo stream probe

This is the next feature to build, in rough sequence. It now also covers finishing the Vimeo exporter itself, not just wiring up what already exists:

1. **Build out the exporter properly**, rather than patching the existing scaffold in place: fix the `INFLUX_*` → `INFLUXDB_*` env var naming, define or import a working `require_env` helper, and give `scripts/vimeo-exporter.py` a real entry point that `ffmpeg/run.sh` can call (either rename it to `monitor.py` or update `run.sh` to call it by name).
2. **Enable the `ffmpeg` service** in `compose.yml` — uncomment it, confirm the `./scripts` volume mount matches what the script expects, and set a sensible default `POLL_INTERVAL`.
3. **Add a Grafana dashboard for stream health** (the current top priority), querying the `stream` measurement's `healthy`, `bitrate`, `codec`, `width`/`height`, and `failure_reason` fields — likely modeled after `device-page.json`.
4. **Verify `make script`** works end-to-end for local debugging once the service is enabled.
5. Fold in results from the [variable review](developer/variable-review.md) so the exporter's environment variables are correct from the start rather than needing another pass later.

See [FFmpeg / Vimeo](developer/ffmpeg-vimeo.md) for the architectural detail behind each of these steps.

## Contributing to this list

Found something else that's broken or misconfigured? Add it to the relevant table above in the same pull request as your fix (or on its own, if you're just documenting it for later). Keeping this page accurate is more valuable than keeping it short.
