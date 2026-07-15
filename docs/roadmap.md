# Roadmap

The stack is being rebuilt as a Prometheus / Grafana server on Cherry (this repo)
with Raspberry Pi exporters in `docker-slice-pi`. Sequencing and done-when criteria
live in `refactor-plan.md` at the repo root; locked architecture is in `refactor.md`.

## Current focus

| Milestone | Status | Summary |
| --- | --- | --- |
| **M1** — Cherry local metrics + dashboard | **Done** | Prometheus + Grafana + `node_exporter`; both targets UP; provisioned dashboard live; justfile + CI/Pages |
| **M2** — Cloudflare hostname guide | In progress | `docs/cloudflare.md`; Cherry Grafana at `mon-grafana.cothrom.ie`; per-exporter hostnames with a `mon-` prefix under `cothrom.ie` |
| **M3** — Slice template | **Done** | Canonical `template/endpoint/` + [Slice](developer/slice.md); promoted to `docker-slice-pi`; frontend reachability verified |
| **M4** — Link slice → Cherry | **Done** | Tailscale scrapes (`*.taild08b87.ts.net:9100/9115`); Grafana via Cloudflare; **Fleet hosts** dashboard |
| **M5** — Light alerting | Optional | Alertmanager + a few rules |
| **G2** — ffprobe exporter | After M4 | Prometheus exporter; auth notes in [FFmpeg / Vimeo](developer/ffmpeg-vimeo.md) |

## Deferred

Apple mirror, speedtest exporter, Web Presenter `json_exporter`, Streaming PC,
long-term storage, and dynamic service discovery.

## Legacy notes

The `telegraf/` directory and future ffprobe scaffolding remain in the repository
but are not part of the running Compose stack. Historical Influx/Telegraf docs
were removed after M1 so the published guide describes only the current system.
