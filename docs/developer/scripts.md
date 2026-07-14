# Scripts

Python helpers under `scripts/`. They are **not** part of the M1 Compose stack.
Dependencies are declared in `pyproject.toml` and installed with `just sync`.

Both scripts use [pyvimeo](https://github.com/vimeo/vimeo.py). Full auth notes and
API pitfalls are documented in [FFmpeg / Vimeo](ffmpeg-vimeo.md).

## `scripts/vimeodata.py`

Working smoke test: authenticates and POSTs to the live-event analytics export
endpoint, then prints JSON.

```bash
just sync
uv run python scripts/vimeodata.py
```

Requires `VIMEO_TOKEN`, `VIMEO_KEY`, `VIMEO_SECRET`, and `VIMEO_EVENTID` in the
environment (or `.env` loaded by your shell).

## `scripts/vimeo-exporter.py`

Scaffold for the future ffprobe exporter (G2). Shows the intended flow
(playback URL → `ffprobe` → metrics) but is **not runnable as-is** (undefined
`require_env`, Influx write path). Reuse the API calls; do not revive Influx for G2.

## Adding a new script

Add dependencies under `[project.dependencies]` in `pyproject.toml`, then
`just sync`. Prefer `uv run python scripts/…` for local checks until the G2
container image is rebuilt.
