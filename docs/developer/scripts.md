# Scripts

Two standalone Python scripts live in `scripts/`, both built around the [pyvimeo](https://github.com/vimeo/vimeo.py) client. Neither is wired into the running stack today — see [FFmpeg / Vimeo](ffmpeg-vimeo.md) for the plan to change that.

## `scripts/vimeodata.py`

A one-off probe that authenticates against the Vimeo API and POSTs to the live event analytics export endpoint:

```
https://api.vimeo.com/live_events/{VIMEO_EVENTID}/export_vpaas_analytics
```

It prints the JSON response to stdout and exits non-zero on any failure. Useful for manually checking that your `VIMEO_TOKEN`/`VIMEO_KEY`/`VIMEO_SECRET`/`VIMEO_EVENTID` credentials work and what analytics data is available, but it doesn't write anything to InfluxDB.

Run it with:

```bash
make script SCRIPT=vimeodata.py
```

(This currently requires the `ffmpeg` service to be enabled, since `make script` runs `docker compose run --rm --entrypoint python ffmpeg scripts/$(SCRIPT)` — see the [Roadmap](../roadmap.md).)

## `scripts/vimeo-exporter.py`

The intended production exporter: fetches the HLS playback URL for a live event, runs `ffprobe` against it, and publishes a `stream` measurement to InfluxDB describing the encoder's actual output (resolution, fps, bitrate, codec, duration) and a derived `healthy` boolean.

High-level flow:

1. `get_hls_url()` — calls the Vimeo API for the event's `m3u8_playback_url`.
2. `probe_stream()` — shells out to `ffprobe -show_streams -show_format` against that URL and parses video/audio stream metadata.
3. `evaluate_health()` — marks the stream unhealthy if the API call failed, the probe failed, or any of resolution/fps/bitrate came back as zero.
4. `publish()` — writes a `stream` point to InfluxDB, tagged by `device` (from `DEVICE_NAME`).

This script is not currently runnable as-is — see [FFmpeg / Vimeo](ffmpeg-vimeo.md) for the known issues blocking it (a missing `require_env` helper and environment variable names that don't match `env.sample`).

## Adding a new script

Scripts are intended to run inside the `ffmpeg` container, which has `ffprobe`, Python, and the dependencies from `pyproject.toml` available. Add new dependencies to `pyproject.toml` under `[project.dependencies]` and run `make sync` to pick them up locally, or rebuild the `ffmpeg` image (`make build SERVICE=ffmpeg`) to pick them up in the container.
