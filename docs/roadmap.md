# Roadmap

The MVP monitoring stack is live: Cherry runs the server stack, Raspberry Pi
endpoints run the slice stack, and Grafana is available to operators through
Cloudflare Access.

## Done (MVP)

- Cherry server stack: Prometheus, Grafana, `node_exporter`, Speedtest Tracker,
  and optional `cloudflared`.
- Slice endpoint stack: `node_exporter`, `blackbox_exporter`, Speedtest Tracker,
  and optional `cloudflared` in `docker-slice-pi`.
- Remote scrapes over Tailscale MagicDNS for `streamrtn1`-`streamrtn4`.
- Grafana for humans at `https://mon-grafana.cothrom.ie`, protected by
  Cloudflare Access.
- Provisioned Cherry host, Fleet hosts, and Speedtest dashboards.

## Later epics

- Alerting: Alertmanager, Prometheus rules, notification routing, and runbook
  links. Treat this as the next major epic when the MVP needs paging.
- Apple mirror: second monitoring server for backup / resilience.
- Additional probes: Apple mirror checks, Web Presenter `json_exporter`, and
  Streaming PC visibility.
- Longer retention and service discovery once the fleet needs them.
- Vimeo HLS / ffprobe exporter: developed in the sibling `exporter-vimeo`
  repository, then scraped by this stack once it exposes Prometheus metrics.
