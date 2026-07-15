# Decisions

This page is the short, published digest of the architecture choices that shape
the project.

## Deployment boundary

- This repository is the monitoring **server stack**, deployed on Cherry.
- `docker-slice-pi` is the reusable endpoint stack for Raspberry Pis, with one
  host-specific `.env` per Pi. The canonical template is reviewed under
  `template/endpoint/` here before copy/promote — see [Slice](slice.md).
- Apple will run a mirror of this server stack later. Host-specific services do
  not belong in this repository.

## Metrics model

- Prometheus pulls metrics from exporters; Grafana queries them with PromQL.
- The old Telegraf/InfluxDB stack was replaced without a dual cutover or
  historical-data migration.
- Static scrape targets are sufficient for the current fleet. Service discovery
  and long-term remote storage are deferred.
- Speedtest Tracker exposes Ookla results through `/prometheus` on Cherry and
  each slice host.

## Network model

- Every stack has project-scoped `frontend` and `backend` Compose networks.
- `cloudflared` joins `frontend` only. Grafana is dual-homed so the tunnel can
  reach it while it queries Prometheus on `backend`.
- **Hybrid link:** Grafana (humans) via Cloudflare Tunnel + Access at
  `mon-grafana.cothrom.ie`. Remote exporter scrapes via **Tailscale MagicDNS**
  (`<HOST_ID>.taild08b87.ts.net:9100` / `:9115`). Slice `cloudflared` is
  optional (Compose profile `tunnel`).
- Restrict exporter host ports with Tailscale ACLs / host firewall — do not
  expose `/metrics` on the public internet.

## Delivery shape

- This repository owns the server stack and the canonical endpoint template.
- `docker-slice-pi` owns deployable Raspberry Pi endpoint files.
- Vimeo HLS / ffprobe exporter work lives in the sibling `exporter-vimeo`
  repository and will be scraped here once it exposes Prometheus metrics.
- Alerting is a later epic: add Alertmanager, rules, and notification routing
  together rather than as incidental config.

## Operational conventions

- Secrets and host-specific values live in `.env`; never commit them.
- Named volumes retain the `NSD_` prefix.
- Production images use deliberate version pins rather than floating `latest`.
- Provisioned Grafana JSON and Prometheus YAML in this repository are the source
  of truth.

See [Cloudflare](../cloudflare.md), [Architecture](architecture.md),
[Prometheus](prometheus.md), and [Roadmap](../roadmap.md) for implementation
details and future epics.
