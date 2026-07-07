# Operations

Day-to-day tasks for running the stack. All commands are `make` targets; run `make help` at any time for the full list.

## Starting and stopping

```bash
make up               # start all services in the background
make up ARGS="--build" # rebuild images before starting
make down             # stop and remove containers (data volumes persist)
make restart          # restart all services
make restart SERVICE=grafana  # restart a single service
```

## Logs and status

```bash
make logs                     # follow logs for every service
make logs SERVICE=telegraf    # follow logs for one service
make ps                       # list running containers
make config                   # print the fully resolved compose configuration
```

`make config` is useful for confirming that environment variable substitution (e.g. `${STREAM1_HOST}`) resolved the way you expect.

## Shelling into a container

```bash
make sh SERVICE=grafana                    # open an interactive shell
make exec SERVICE=telegraf CMD="telegraf --test"  # run a one-off command
```

## Updating images

```bash
make pull    # pull the latest images for all services
make build   # rebuild locally-built images (telegraf, ffmpeg)
make rebuild # rebuild without cache and force-recreate containers
```

## Backing up data

All persistent state lives in Docker volumes prefixed `NSD_`:

- `NSD_influxdb2-data`, `NSD_influxdb2-config` — metrics and InfluxDB configuration
- `NSD_grafana_data` — Grafana dashboards, users, and settings (though dashboards themselves are provisioned from `grafana/dashboards/` and can be recreated)
- `NSD_speedtest-tracker-data` — Speedtest Tracker's SQLite database

Back these up with `docker run --rm -v NSD_influxdb2-data:/data -v $(pwd):/backup alpine tar czf /backup/influxdb2-data.tar.gz -C /data .` (repeat per volume), or use your preferred Docker volume backup tool.

## Removing everything

```bash
make clean
```

This stops the stack, removes every `NSD_*` volume, and prunes unused Docker resources (`docker system prune -f`). This is destructive and cannot be undone — use it when you want a completely fresh start, such as after changing `INFLUXDB_ORG`/`INFLUXDB_BUCKET`.
