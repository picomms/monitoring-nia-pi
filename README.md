# NIA Monitoring

Docker Compose monitoring server stack for live-streaming infrastructure.
Prometheus scrapes metrics, Grafana renders provisioned dashboards. Primary host:
**Cherry**.

## Quick start

Prerequisites: Docker, Docker Compose, and [just](https://github.com/casey/just).

```bash
cp env.sample .env
# set GF_ADMIN_PASSWORD (and friends)
just up
```

Open Grafana at [http://localhost:3000](http://localhost:3000) (see `GRAFANA_PORT`
in `.env`). **Cherry host** shows local metrics; **Fleet hosts** covers Cherry
plus slice Pis scraped over Tailscale. Public Grafana:
`https://mon-grafana.cothrom.ie`.

| Service | Default URL | Purpose |
| --- | --- | --- |
| Grafana | `http://localhost:3000` | Dashboards |
| Prometheus | `http://localhost:9090` | Targets / PromQL |

Optional Cloudflare Tunnel for Grafana: set `TUNNEL_TOKEN` and run `just up-tunnel`.

## Common commands

```bash
just --list    # all recipes
just logs      # follow logs
just ps
just down
just docs-serve
just docs-build
```

## Documentation

Published at [https://picomms.github.io/monitoring-nia-pi/](https://picomms.github.io/monitoring-nia-pi/).
Source: [github.com/picomms/monitoring-nia-pi](https://github.com/picomms/monitoring-nia-pi).

Start with the published
[architecture](docs/developer/architecture.md),
[decisions](docs/developer/decisions.md), and
[Prometheus operations](docs/developer/prometheus.md). Tunnel and DNS setup is in
[Cloudflare](docs/cloudflare.md). The complete decision record and milestone
sequence are [`refactor.md`](refactor.md) and [`refactor-plan.md`](refactor-plan.md).
Vimeo auth notes for the future ffprobe exporter live in
[docs/developer/ffmpeg-vimeo.md](docs/developer/ffmpeg-vimeo.md).

## License

MIT — see [LICENSE](LICENSE).

