# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project summary

NIA Stream Dashboard is a Docker Compose monitoring platform for live-streaming infrastructure: Telegraf collects metrics from Web Presenter encoders, Speedtest Tracker, and the host network, InfluxDB 2 stores them, and Grafana renders them on provisioned dashboards. An FFmpeg-based service to probe Vimeo HLS streams directly is under active development but not yet enabled. Full documentation lives under `docs/` (see `mkdocs.yml`) and is published at https://picommcapp.github.io/NIA-stream-dashboard/.

## Repo map

| Path             | What it is                                                                                    |
| ---------------- | --------------------------------------------------------------------------------------------- |
| `compose.yml`    | The whole stack definition (Compose project `stream-dashboard`)                               |
| `Makefile`       | All common workflows — run `make help` before reaching for raw `docker compose`/`uv` commands |
| `env.sample`     | Template for `.env`; **incomplete**, see `docs/roadmap.md`                                    |
| `telegraf/`      | Telegraf image + `telegraf.conf` (all metric collection config)                               |
| `grafana/`       | Provisioned datasource + dashboard JSON files (source of truth — UI edits don't persist)      |
| `ffmpeg/`        | Planned Vimeo stream probe container (not yet enabled in `compose.yml`)                       |
| `scripts/`       | Python scripts for Vimeo API/HLS probing, meant to run inside the `ffmpeg` container          |
| `docs/`          | MkDocs source; user guide + developer guide + roadmap                                         |
| `pyproject.toml` | Python deps for `scripts/` and the docs toolchain, managed with `uv`                          |

## Common commands

```bash
make up             # start the stack
make logs           # follow logs
make config         # print resolved compose config (good for debugging env var substitution)
make sync           # install Python deps (uv sync --all-extras)
make docs-serve     # preview docs locally at :8000
make docs-build     # strict docs build, used in CI
```

## Conventions

- Environment variables live in `.env` (gitignored), templated from `env.sample`. Never commit `.env` or real secrets.
- Docker volumes are prefixed `NSD_` — don't introduce unprefixed volumes.
- Grafana dashboards are edited as JSON files in `grafana/dashboards/`, not through the Grafana UI (UI changes are reverted by provisioning). Use stable, human-readable `uid` values, not auto-generated ones.
- InfluxDB measurement names in use: `PingChecks`, `NetworkInterfaces`, `NetworkStats`, `VimeoResponse`, `VimeoDNSQuery`, `SpeedTest`, `WP1`–`WP8`, and `stream` (planned). Keep new measurements consistent with this flat, per-source naming style rather than introducing heavy tagging.
- Flux (not InfluxQL) is the query language used throughout Grafana dashboards.

## Known pitfalls (see `docs/roadmap.md` for the full list)

- The Grafana InfluxDB datasource expects org/bucket `nia`, but Compose defaults to `default` — check both when debugging "no data" in Grafana.
- `telegraf.conf` reads `SPEEDTEST_API_ACCESS_TOKEN`, but `env.sample` only has `SPEEDTEST_TRACKER_API_TOKEN`.
- `STREAM1_HOST`–`STREAM8_HOST` are required by Telegraf but absent from `env.sample`.
- `scripts/vimeo-exporter.py` uses `INFLUX_*` variable names instead of `INFLUXDB_*`, and calls an undefined `require_env()`.
- The `ffmpeg` service is commented out in `compose.yml`; its entry point (`ffmpeg/run.sh`) calls a `monitor.py` that doesn't exist.

## Scope guidance for agents

- Documentation changes (README, `docs/`, `AGENTS.md`) can be made freely.
- Config fixes (env var alignment, enabling the `ffmpeg` service, dashboard changes) should be treated as real feature work — read `docs/roadmap.md` first, and update it when you resolve an item there.
- When touching `telegraf.conf`, `grafana/datasources/influxdb.yml`, or `env.sample`, check the other two for consistency — they're tightly coupled.

## Do not

- Force-push to `main`.
- Commit `.env` or any file containing real tokens/credentials.
- Run `make clean` unless the user explicitly asks for it — it deletes all `NSD_*` volumes, including InfluxDB's metric history.
