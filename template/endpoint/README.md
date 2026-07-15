# NIA Monitoring — endpoint stack

Reusable Compose template for Raspberry Pi exporters. One shared repo
([`docker-slice-pi`](https://github.com/picomms/docker-slice-pi)); unique `.env`
per host.

**Documentation (source of truth)** lives in the server repo:

- [Slice template](https://picomms.github.io/monitoring-nia-pi/developer/slice/)
- [Cloudflare (Grafana only)](https://picomms.github.io/monitoring-nia-pi/cloudflare/)

## Quick start

```bash
cp env.sample .env
# set HOST_ID (e.g. streamrtn1) and SPEEDTEST_APP_KEY
just up
just ps
```

Cherry scrapes over **Tailscale** on published ports:

| Port | Service |
| --- | --- |
| `9100` | `node_exporter` |
| `9115` | `blackbox_exporter` |
| `8765` | `speedtest-tracker` (UI + `/prometheus`) |

Generate `SPEEDTEST_APP_KEY` (unique per host):

```bash
# any machine with Docker:
openssl rand -base64 32 | sed 's/^/base64:/'
```

Restrict ports with Tailscale ACLs / host firewall. Optional tunnel: set
`TUNNEL_TOKEN` and `just up-tunnel` (not required for scrapes).

## Verify locally

```bash
curl -sS http://127.0.0.1:9100/metrics | head
curl -sS http://127.0.0.1:9115/metrics | head
curl -sS http://127.0.0.1:8765/prometheus | head
```

From Cherry (MagicDNS):

```bash
curl -sS "http://<HOST_ID>.taild08b87.ts.net:9100/metrics" | head
curl -sS "http://<HOST_ID>.taild08b87.ts.net:8765/prometheus" | head
```
