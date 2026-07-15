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

## Fleet hosts

- **File:** `grafana/dashboards/fleet-hosts.json`
- **UID:** `fleet-hosts`
- **Folder:** NIA Monitoring

Fleet panels cover Cherry plus `streamrtn1`-`streamrtn4` over Tailscale:

- Host availability
- CPU and memory
- Filesystem usage
- Network receive / transmit rates
- ICMP probe status via each slice blackbox exporter

## Speedtest

- **File:** `grafana/dashboards/speedtest.json`
- **UID:** `speedtest`
- **Folder:** NIA Monitoring

Speedtest Tracker exports Ookla results from Cherry and each slice host. Metrics
remain empty until each tracker completes its first scheduled or manual test.
