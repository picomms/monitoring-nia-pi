# NIA Stream Dashboard

A self-hosted monitoring platform for live-streaming infrastructure. It tracks network health, ISP speed, and up to eight Blackmagic Web Presenter encoders, with a Vimeo/FFmpeg stream probe in active development.

The stack runs entirely in Docker Compose: Telegraf collects metrics, InfluxDB stores them, and Grafana renders the dashboards.

## Quick start

Prerequisites: Docker, Docker Compose, and Make.

```bash
cp env.sample .env
# edit .env with your InfluxDB/Grafana credentials, device hosts, and Vimeo keys
make up
```

Once the stack is healthy, open Grafana at [http://localhost:3000](http://localhost:3000) (default `${GRAFANA_PORT}`, see `.env`).

| Service | Default URL | Purpose |
|---|---|---|
| Grafana | `http://localhost:3000` | Dashboards |
| InfluxDB | `http://localhost:8086` | Metrics storage / admin UI |
| Speedtest Tracker | `http://localhost:8087` | Scheduled ISP speed tests |

## Common commands

```bash
make help      # list all available targets
make logs      # follow logs for all services
make ps        # list running containers
make down      # stop the stack
make clean     # stop the stack and remove NSD_* volumes
```

## Documentation

Full documentation, including setup guides, configuration reference, architecture, and the project roadmap, is published at [https://picommcapp.github.io/NIA-stream-dashboard/](https://picommcapp.github.io/NIA-stream-dashboard/).

To preview the docs locally:

```bash
make install      # one-time: install uv
make sync         # install runtime + docs dependencies
make docs-serve   # serve docs at http://localhost:8000
```

## Project status

The core monitoring stack (Telegraf, InfluxDB, Grafana, Speedtest Tracker) has reached MVP. A handful of configuration mismatches and an FFmpeg-based Vimeo stream probe are still in progress — see the [roadmap](https://picommcapp.github.io/NIA-stream-dashboard/roadmap/) for details.

## License

MIT — see [LICENSE](LICENSE).
