# Refactor plan — milestones

Working plan for implementing the architecture in [`refactor.md`](refactor.md).
Keep this list short; add work only when a milestone is blocked without it.

## Principles

- **Architecture lives in `refactor.md`.** This file is sequencing only.
- **Greenfield.** Replace the old Influx/Telegraf stack; do not run a dual cutover.
- **Local first, then link.** Get useful metrics and a dashboard on Cherry
  (this repo's server stack) before chasing remote exporters or custom tooling.
- **Stock before bespoke.** Node + blackbox (and tunnels) before the ffprobe
  exporter — ffprobe is **second generation**.
- **Defer by default.** Apple mirror, Streaming PC, speedtest, Web Presenters,
  fancy SD, long-term storage, and polish wait until the core path works.

## Milestones

### M1 — Cherry local metrics + dashboard

Stand up this repo's server Compose with `frontend` / `backend` on Cherry:

- Prometheus + Grafana
- Local host/network metrics on Cherry (e.g. `node_exporter` in this stack)
- A small provisioned dashboard that shows those metrics
- `cloudflared` for Grafana Access when ready (can land in the same milestone
  or immediately after the dashboard works on the LAN)
- `justfile`, basic CI (`compose config` + docs strict build), GitHub Pages deploy
- Vimeo auth / API notes preserved in `docs/developer/ffmpeg-vimeo.md` for G2

**Done when:** Cherry shows live local metrics in Grafana without depending on
any RPi or custom exporter.

Skip Alertmanager, remote scrape jobs, and fancy boards.

**Status:** Done — verified on Cherry (`just up`; `node` + `prometheus` targets UP;
provisioned **Cherry host** dashboard live with host metrics).

### M2 — Cloudflare hostname guide (thin)

Write `docs/cloudflare.md` with only what we need for the link:

- Remotely managed tunnel + `TUNNEL_TOKEN` (Cherry Grafana + each RPi)
- Hostname → Compose service on `frontend`
- How Prometheus scrapes remote exporter hostnames

**Done when:** tunnels/DNS/tokens can be created from the doc without guessing.

Settle the hostname scheme here. Do not expand into a full Zero Trust handbook.

### M3 — Slice template compose (`docker-slice-pi`)

One shared repo; unique `.env` per RPi. Template stack only:

- `frontend` / `backend` networks
- `cloudflared`
- `node_exporter`
- `blackbox_exporter` (config stub for the probes we care about)

**Done when:** the template is documented and `compose up` works on a pilot RPi
with exporters reachable on `frontend` (even before Cherry scrapes them).

No ffprobe, no speedtest in the template yet.

### M4 — Link slice → Cherry (network / blackbox only)

- Tunnel hostnames for node + blackbox on the pilot RPi
- Static scrape jobs on Cherry Prometheus
- Extend the Cherry dashboard just enough to show remote host + probe health

**Done when:** central Prometheus scrapes the pilot RPi’s node and blackbox
metrics over hostname routes, and Grafana shows them.

Roll the same template to other RPis only after the pilot path is solid.

### M5 — Light alerting (optional stretch)

Alertmanager + a few rules (`up == 0`, blackbox probe failed). Document in
`docs/alerting.md` as added.

**Done when:** a test alert fires through the chosen notification path.

Skip if it would distract from locking M1–M4.

## Second generation

### G2 — ffprobe exporter

Build the Prometheus ffprobe/Vimeo exporter in `monitoring-nia-pi`, add it to
the slice template, scrape via tunnel hostname, then dashboard panels.

**Start only after** M4 is working. Treat as its own small plan when we get there.

## Later (not in M1–M5)

- Apple mirror of this server stack (backup)
- Speedtest exporter
- Web Presenter `json_exporter`
- Streaming PC stack
- Long-term storage / remote write
- Dynamic service discovery

## Suggested order of work

```text
M1  Cherry local metrics + dashboard     ← first useful win
 → M2  Cloudflare hostname guide
 → M3  Slice template (node + blackbox + cloudflared)
 → M4  Scrape pilot RPi from Cherry        ← first remote end-to-end win
 → M5  Light alerting (if needed)
 —— then ——
G2  ffprobe exporter + panels
```

Revisit this file only when a milestone finishes or a locked decision in
`refactor.md` changes.
