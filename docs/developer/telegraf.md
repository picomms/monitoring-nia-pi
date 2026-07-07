# Telegraf

Telegraf is the sole metrics collector in the stack. Its configuration lives entirely in `telegraf/telegraf.conf`, which is mounted read-only into the container.

## Image

`telegraf/Dockerfile` extends the official `telegraf:latest` image with `curl`, `jq`, `iputils-ping`, and `ntpstat`, which some plugins (or future scripts) shell out to.

## Agent settings

```toml
[agent]
  interval = "10s"
  flush_interval = "10s"
```

All inputs are polled and flushed every 10 seconds. `omit_hostname = true` keeps the `host` tag off every point, since this stack monitors a single site rather than a fleet.

## Output

A single `outputs.influxdb_v2` block writes every measurement to the bucket/org defined by `INFLUXDB_ORG` / `INFLUXDB_BUCKET`, authenticated with `INFLUXDB_ADMIN_TOKEN`.

## Inputs

### Network health

| Plugin | `name_override` | What it does |
|---|---|---|
| `inputs.ping` | `PingChecks` | ICMP ping (4 packets, native method) against Vimeo, YouTube, and configured DNS resolvers |
| `inputs.net` | `NetworkInterfaces` | Per-interface byte/error/drop counters, filtered by `NETWORK_INTERFACE` glob patterns |
| `inputs.netstat` | `NetworkStats` | TCP/UDP socket state counts |
| `inputs.net_response` | `VimeoResponse` | TCP connect timing to `vimeo.com:443` |
| `inputs.dns_query` | `VimeoDNSQuery` | DNS resolution timing for `vimeo.com` against the configured resolvers |

### Speedtest Tracker

A single `inputs.http` block polls `http://speedtest-tracker:80/api/v1/results/latest` and maps the JSON response into the `SpeedTest` measurement using `json_v2`, authenticated with a bearer token from `${SPEEDTEST_API_ACCESS_TOKEN}`.

!!! warning
    This variable name doesn't match anything in `env.sample` (which has `SPEEDTEST_TRACKER_API_TOKEN`). See the [Roadmap](../roadmap.md).

### Web Presenters

Eight nearly identical `inputs.http` blocks (`WP1`–`WP8`) each poll two endpoints on a device host:

```
http://${STREAM<n>_HOST}/control/api/v1/livestreams/0
http://${STREAM<n>_HOST}/control/api/v1/livestreams/0/activePlatform
```

Response fields are parsed as JSON strings (`status`, `platform`, `quality`, `server`) into a measurement named `WP<n>`. If `STREAM<n>_HOST` is unset, the HTTP request fails silently and that device's panels simply show no data.

## Processors

```toml
[[processors.rename]]
  namepass = ["WP*"]
  [[processors.rename.replace]]
    field = "bitrate"
    dest = "videoBitrate"
  [[processors.rename.replace]]
    field = "platform"
    dest = "name"
```

This renames fields on every `WP*` measurement so Grafana panels can query consistent field names (`videoBitrate`, `name`) regardless of what the Web Presenter API calls them natively.

## Adding a new device

1. Add `STREAM9_HOST=192.168.1.x` to `.env`.
2. Copy one of the existing `[[inputs.http]]` blocks in `telegraf/telegraf.conf`, bump the variable and `name_override` to `WP9`.
3. Add a corresponding row to `grafana/dashboards/device-overview.json` and an entry to the `device` template variable in `grafana/dashboards/device-page.json` (see [Grafana](grafana.md)).
4. `make restart SERVICE=telegraf` to pick up the config change.
