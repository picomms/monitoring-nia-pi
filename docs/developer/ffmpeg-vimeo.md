# FFmpeg / Vimeo

Second-generation work (G2): a long-lived Prometheus exporter that probes Vimeo HLS
output with `ffprobe`. **Not part of M1** — the Cherry stack today is Prometheus +
Grafana + `node_exporter` only. Keep this page as the source of truth for Vimeo
authentication and the API call patterns that already work, so G2 does not have to
rediscover them.

Architecture lock-in for G2 lives in `refactor.md` at the repo root (Prometheus
client, background probe interval, string fields as labels). Sequencing is in
`refactor-plan.md`. See also the [Roadmap](../roadmap.md).

## Why a separate exporter

- Probing an HLS stream (Vimeo API → `ffprobe`) takes seconds and must not run
  synchronously on a Prometheus scrape.
- The logic is a small Python loop, not a Telegraf plugin.
- Endpoint Pis will eventually run this image from the slice template; the server
  stack only scrapes `/metrics`.

## Scaffolding still on disk

| Piece | File | Notes |
| --- | --- | --- |
| Base image | `ffmpeg/Dockerfile` | FFmpeg + uv deps; not wired into Compose |
| Poll loop | `ffmpeg/run.sh` | Calls `/app/monitor.py` (missing) |
| Exporter scaffold | `scripts/vimeo-exporter.py` | Influx write path; broken `require_env`; keep for API flow |
| Smoke test | `scripts/vimeodata.py` | **Working** auth + analytics POST |

G2 will replace the Influx write path with `prometheus-client` gauges/labels. Do not
revive Influx for this feature.

## Vimeo authentication (working pattern)

pyvimeo's `VimeoClient` needs **all three** of:

| Env var | Role |
| --- | --- |
| `VIMEO_TOKEN` | Personal/access token |
| `VIMEO_KEY` | App client ID |
| `VIMEO_SECRET` | App client secret |

```python
from vimeo import VimeoClient

client = VimeoClient(
    token=os.environ["VIMEO_TOKEN"],
    key=os.environ["VIMEO_KEY"],
    secret=os.environ["VIMEO_SECRET"],
)
```

### Auth pitfalls

- **Token alone is not enough** for this client setup — key and secret are required
  with the patterns below.
- Create the app and token in the Vimeo developer console with scopes that allow
  live-event read/export for your account.
- Event IDs are per live event; a wrong ID yields HTTP errors, not empty success.
- Paths differ: analytics uses `/live_events/{id}/…` while playback uses
  `/me/live_events/{id}/…`. Copy paths carefully.

Commented placeholders for these vars live in `env.sample` under “for later (G2)”.

## Working API examples

### 1. Credential smoke test — `scripts/vimeodata.py`

Authenticates with the triple above and **POSTs** (GET is rejected) to:

```text
https://api.vimeo.com/live_events/{VIMEO_EVENTID}/export_vpaas_analytics
```

Prints JSON on success; exits non-zero on failure. Use this before building G2.

Run locally (after `just sync` and a filled `.env`):

```bash
uv run python scripts/vimeodata.py
```

### 2. HLS playback URL — exporter scaffold

`scripts/vimeo-exporter.py` (scaffold) fetches the playable HLS URL with:

```text
GET https://api.vimeo.com/me/live_events/{VIMEO_EVENTID}/m3u8_playback
```

Response field of interest: `m3u8_playback_url`. That URL is what `ffprobe` should
target. The scaffold then shells out to `ffprobe -show_streams -show_format` and
evaluates health from resolution / fps / bitrate.

The scaffold still writes Influx and calls an undefined `require_env` — treat it as
an API flowchart, not a runnable exporter.

## Intended G2 flow

```mermaid
sequenceDiagram
  participant Loop as exporter poll loop
  participant Vimeo as Vimeo API
  participant Probe as ffprobe
  participant Prom as /metrics

  loop every POLL_INTERVAL
    Loop->>Vimeo: GET me/live_events/{id}/m3u8_playback
    Vimeo-->>Loop: m3u8_playback_url
    Loop->>Probe: ffprobe hls_url
    Probe-->>Loop: stream metadata
    Loop->>Prom: update gauges and labels
  end
```

Prometheus scrapes the exporter over the Cloudflare hostname route (after M4), not
during the probe itself.

## Sanity-check checklist (before G2)

1. Set `VIMEO_TOKEN`, `VIMEO_KEY`, `VIMEO_SECRET`, `VIMEO_EVENTID` in `.env`.
2. `uv run python scripts/vimeodata.py` returns 200 JSON.
3. Manually `client.get` the `m3u8_playback` URL (or temporarily uncomment / fix
   `get_hls_url` in the scaffold) and confirm `m3u8_playback_url` is present.
4. Run `ffprobe` against that URL once on a machine with FFmpeg installed.

Only then implement the Prometheus exporter.
