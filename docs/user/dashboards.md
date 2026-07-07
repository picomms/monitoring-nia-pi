# Dashboards

Grafana provisions four dashboards automatically from `grafana/dashboards/`, grouped in a folder called **NIA Stream**. They are read-only from the UI's perspective — any changes made in the Grafana UI will be reverted on the next provisioning sync, since the JSON files in the repo are the source of truth. See [Grafana](../developer/grafana.md) for how to edit them.

## General

**File:** `grafana/dashboards/general.json`

A top-level summary combining ISP speed, network health, and device status in one view:

- Download/upload speed, ping, and packet loss (from Speedtest Tracker)
- Active TCP connection count
- Interface traffic rate and ping response time across all monitored targets
- A table summarizing the latest status of all eight Web Presenters

Links to **Network Health** and **Device Overview** are available in the dashboard's top-right menu.

## Network Health

**File:** `grafana/dashboards/network-health.json`

A deeper look at connectivity, independent of any specific device:

- Interface traffic rate and error/drop counters
- Ping latency and packet loss per target (Vimeo, YouTube, DNS resolvers)
- Vimeo TCP response time and DNS query time
- TCP connection state counts
- Full speed test history (download, upload, ping, packet loss)

## Device Overview

**File:** `grafana/dashboards/device-overview.json`

One row per Web Presenter (WP1–WP8), each showing:

- Live status (Streaming / Idle / Disconnected)
- Current video bitrate
- Cache level
- Active output platform

A device with no `STREAM<n>_HOST` configured (see [Configuration](configuration.md)) will show no data in its row rather than an error.

## Device Page

**File:** `grafana/dashboards/device-page.json`

A detailed, single-device view driven by the `$device` template variable (WP1–WP8, selectable from the dashboard's top bar):

- Live status, video/audio bitrate, cache, and stream duration
- Bitrate history over time
- Active platform details table
- Cache and stream duration history

Use the **Back to Device Overview** link at the top to return to the summary view.

## Planned: stream health dashboard

Once the FFmpeg/Vimeo probe (see [FFmpeg / Vimeo](../developer/ffmpeg-vimeo.md)) is wired in, its `stream` measurement (bitrate, codec, resolution, `healthy`, `failure_reason`) has no corresponding Grafana panels yet. Adding a stream health dashboard is tracked in the [Roadmap](../roadmap.md).
