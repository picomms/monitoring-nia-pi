# Decisions

This page is the short, published digest of the architecture choices that shape
the project. The full decision record lives in `refactor.md` at the repository
root; sequencing and done criteria live in `refactor-plan.md`.

## Deployment boundary

- This repository is the monitoring **server stack**, deployed on Cherry.
- `docker-slice-pi` is the reusable endpoint stack for Raspberry Pis, with one
  host-specific `.env` per Pi.
- Apple will run a mirror of this server stack later. Host-specific services do
  not belong in this repository.

## Metrics model

- Prometheus pulls metrics from exporters; Grafana queries them with PromQL.
- The old Telegraf/InfluxDB stack was replaced without a dual cutover or
  historical-data migration.
- Static scrape targets are sufficient for the current fleet. Service discovery
  and long-term remote storage are deferred.

## Network model

- Every stack has project-scoped `frontend` and `backend` Compose networks.
- `cloudflared` joins `frontend` only. Grafana is dual-homed so the tunnel can
  reach it while it queries Prometheus on `backend`.
- Remote exporters will be scraped through stable, hostname-based Cloudflare
  Tunnel routes. Tailscale and private-CIDR/WARP routing are not part of the
  monitoring data path.
- The exact hostname and Access policy scheme is the M2 deliverable.

## Delivery order

- Use stock exporters first: `node_exporter`, then `blackbox_exporter`.
- Prove the local Cherry path before linking Raspberry Pis.
- The Vimeo/ffprobe exporter is second-generation work after the remote
  node/blackbox path works through M4.

## Operational conventions

- Secrets and host-specific values live in `.env`; never commit them.
- Named volumes retain the `NSD_` prefix.
- Production images use deliberate version pins rather than floating `latest`.
- Provisioned Grafana JSON and Prometheus YAML in this repository are the source
  of truth.

See the [Architecture](architecture.md), [Prometheus](prometheus.md), and
[Roadmap](../roadmap.md) for the current implementation and next steps.
