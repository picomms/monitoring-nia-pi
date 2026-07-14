# Dashboards

Grafana provisions dashboards from `grafana/dashboards/`. Edits made in the UI
are overwritten on the next provisioning sync — treat the JSON files in git as
source of truth.

## Cherry host

- **File:** `grafana/dashboards/cherry-host.json`
- **UID:** `cherry-host`
- **Folder:** NIA Monitoring

Live Cherry host metrics from `node_exporter`:

- CPU utilisation
- Memory used / total
- Root filesystem used / total
- Network receive / transmit rates (non-loopback)

Datasource: provisioned Prometheus (`uid: prometheus`).

## Later

Remote RPi node/blackbox panels arrive with milestone M4. Stream/ffprobe panels
wait for G2 — see [FFmpeg / Vimeo](../developer/ffmpeg-vimeo.md).
