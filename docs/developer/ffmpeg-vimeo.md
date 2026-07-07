# FFmpeg / Vimeo

The next feature being built on top of the MVP monitoring stack: an FFmpeg-based container that probes the actual Vimeo HLS output of each encoder, rather than just the encoder's own self-reported status (which is all the Web Presenter API in [Telegraf](telegraf.md) currently gives us).

## Why a separate service

Telegraf handles everything else in this stack, but it can't do this job on its own:

- It has no `ffprobe`/`ffmpeg` binary, and adding one would bloat every Telegraf deployment for a feature only this stack needs.
- Probing an HLS stream (fetching the Vimeo API, then running `ffprobe` against the resulting URL) takes meaningfully longer than the 10-second interval used for every other input, and shouldn't block the rest of Telegraf's collection loop.
- The logic is naturally a small Python script (API call + subprocess + health evaluation) rather than a declarative Telegraf plugin config.

So it runs as its own container with a simple poll loop, publishing to the same InfluxDB instance as everything else.

## Current state

The foundation exists but the service is **not enabled**:

```yaml
# FFMPEG DISABLED FOR NOW
# ffmpeg:
#   image: jrottenberg/ffmpeg:8.1-ubuntu
#   ...
```

| Piece | File | Status |
|---|---|---|
| Base image | `ffmpeg/Dockerfile` | Builds on `jrottenberg/ffmpeg:8.1-ubuntu`, installs `uv`, and `pip install`s `pyvimeo`, `dotenv`, `influxdb-client` |
| Poll loop | `ffmpeg/run.sh` | Loops every `POLL_INTERVAL` seconds (default 60), calling `python /app/monitor.py` |
| Exporter logic | `scripts/vimeo-exporter.py` | Implements the actual probe (Vimeo API → `ffprobe` → InfluxDB write) — see [Scripts](scripts.md) |

These three pieces don't yet connect: `run.sh` calls `/app/monitor.py`, which doesn't exist, and the compose service that would mount `scripts/` into the container is commented out. `vimeo-exporter.py` is genuinely just scaffolding rather than a finished feature — it calls a `require_env()` that's never defined, and uses different environment variable names (`INFLUX_URL`, `INFLUX_ADMIN_TOKEN`, `INFLUX_ORG`, `INFLUX_BUCKET`) than the rest of the stack (`INFLUXDB_*`). See the [Variable Review](variable-review.md) for the full audit of naming across the stack before renaming anything here.

## How it's meant to work

```mermaid
sequenceDiagram
  participant Loop as run.sh (poll loop)
  participant Vimeo as Vimeo API
  participant Probe as ffprobe
  participant Influx as InfluxDB

  loop every POLL_INTERVAL seconds
    Loop->>Vimeo: GET live_events/{id}/m3u8_playback
    Vimeo-->>Loop: HLS playback URL
    Loop->>Probe: ffprobe <hls_url>
    Probe-->>Loop: stream metadata (codec, fps, bitrate, resolution)
    Loop->>Influx: write "stream" point (healthy, bitrate, codec, failure_reason, ...)
  end
```

The `stream` measurement is tagged by `device` (`DEVICE_NAME`), so a future multi-encoder setup could run one `ffmpeg` container per device with a different `DEVICE_NAME` each.

## What's left to do

See the [Roadmap](../roadmap.md) for the tracked list, but at a high level: align environment variable names, fix or rename the exporter entry point so `run.sh` can call it, uncomment and correctly mount the `ffmpeg` service in `compose.yml`, and add a Grafana dashboard for the `stream` measurement.
