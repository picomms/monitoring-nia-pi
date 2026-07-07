# Getting Started

## Prerequisites

- Docker and Docker Compose
- GNU Make
- Network access to the devices you want to monitor (Web Presenters, speed test servers, Vimeo)

## 1. Configure your environment

Copy the sample environment file and fill in your values:

```bash
cp env.sample .env
```

At minimum, review and set:

- `INFLUXDB_ADMIN_TOKEN`, `INFLUXDB_USER`, `INFLUXDB_PASSWORD` — pick strong values, these seed the InfluxDB instance on first boot
- `GF_ADMIN_USER`, `GF_ADMIN_PASSWORD` — Grafana login
- `SPEEDTEST_TRACKER_HOST` — set to this machine's LAN IP if you'll access it remotely

See the full [Configuration](configuration.md) reference for every variable, including the Web Presenter host variables that aren't yet in `env.sample`.

## 2. Start the stack

```bash
make up
```

This runs `docker compose up -d`, building the `telegraf` image on first run. Check that everything started cleanly:

```bash
make ps
make logs
```

## 3. Open Grafana

Visit `http://localhost:${GRAFANA_PORT}` (default `3000`) and log in with the `GF_ADMIN_USER` / `GF_ADMIN_PASSWORD` you set in `.env`. Three dashboards are provisioned automatically under the **NIA Stream** folder — see [Dashboards](dashboards.md) for what each one shows.

## 4. Verify data is flowing

- The **General** dashboard should show your ISP ping/speed within a few minutes (Speedtest Tracker runs every 10 minutes by default).
- The **Network Health** dashboard should show ping latency and interface traffic immediately, since those come from the host and don't require any external device configuration.
- The **Device Overview** dashboard will stay empty until you configure `STREAM1_HOST`–`STREAM8_HOST` for your Web Presenters (see [Configuration](configuration.md)).

If a panel stays empty longer than expected, check `make logs SERVICE=telegraf` for connection errors, and see the [Roadmap](../roadmap.md) for known configuration mismatches that can cause this.

## Stopping and cleaning up

```bash
make down    # stop containers, keep data
make clean   # stop containers and remove all NSD_* volumes (destructive)
```
