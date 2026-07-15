# Slice template

The endpoint stack for Raspberry Pis. One shared deploy repo
([`docker-slice-pi`](https://github.com/picomms/docker-slice-pi)); unique `.env`
per host. This page is the operator contract.

Cherry scrapes exporters over **Tailscale** (published host ports). Grafana for
humans stays on Cloudflare (`mon-grafana.cothrom.ie`) — see
[Cloudflare](../cloudflare.md).

## Canonical files vs deploy copy

| Location | Role |
| --- | --- |
| [`template/endpoint/`](https://github.com/picomms/monitoring-nia-pi/tree/main/template/endpoint) in this repo | Canonical template to review before promote |
| [`docker-slice-pi`](https://github.com/picomms/docker-slice-pi) | Deploy copy on each RPi |

When promoting a change: edit `template/endpoint/` here, update this page if the
contract changes, then copy the template files into `docker-slice-pi`.

## File map

| Path | Purpose |
| --- | --- |
| `compose.yml` | `node_exporter`, `blackbox_exporter`; optional `cloudflared` (profile `tunnel`) |
| `env.sample` | `HOST_ID`, optional `TUNNEL_TOKEN`, image pins |
| `blackbox/blackbox.yml` | Probe modules (`http_2xx`, `icmp`, `tcp_connect`) — no targets |
| `justfile` | `up` / `up-tunnel` / `down` / `ps` / `logs` / `config` |
| `README.md` | Quick start + link back to these docs |

## Env contract

| Variable | Example | Purpose |
| --- | --- | --- |
| `HOST_ID` | `streamrtn1` | Matches Tailscale hostname / Prometheus `instance` |
| `TUNNEL_TOKEN` | secret | Optional — only for `just up-tunnel` |
| `CLOUDFLARED_VERSION` | `2026.7.1` | Image pin |
| `NODE_EXPORTER_VERSION` | `v1.12.0` | Image pin |
| `BLACKBOX_EXPORTER_VERSION` | `v0.28.0` | Image pin |

Compose layout is identical on every Pi. Do not branch YAML per host — put
differences in `.env` only.

## Scrape path (Tailscale)

| Port | Service | Cherry target |
| --- | --- | --- |
| `9100` | `node_exporter` | `http://<HOST_ID>.taild08b87.ts.net:9100` |
| `9115` | `blackbox_exporter` | `http://<HOST_ID>.taild08b87.ts.net:9115` |

Restrict these ports with **Tailscale ACLs** and/or host firewall so they are
not reachable from the public internet. Current fleet: `streamrtn1`–`streamrtn4`
(see `prometheus/targets/` on the server).

Optional Cloudflare Public Hostnames (`mon-node-*` / `mon-blackbox-*`) are
**not** used for scrapes. Use `just up-tunnel` only if you still want them for
debug.

## Networks

Project-scoped `frontend` and `backend` only. Do **not** pin bare external names
like `name: frontend`.

| Service | Network | Notes |
| --- | --- | --- |
| `node_exporter` | `frontend` | Host port `9100` for Tailscale scrapes |
| `blackbox_exporter` | `frontend` | Host port `9115` |
| `cloudflared` | `frontend` | Profile `tunnel` only |

## Bring-up

```bash
cp env.sample .env
# set HOST_ID (e.g. streamrtn1)
just up
just ps
```

### Local metrics check

```bash
curl -sS http://127.0.0.1:9100/metrics | head
curl -sS http://127.0.0.1:9115/metrics | head
```

### From Cherry over Tailscale

```bash
curl -sS "http://streamrtn1.taild08b87.ts.net:9100/metrics" | head
```

### Roll ports to several Pis (from Cherry)

```bash
chmod +x scripts/roll-slice-ports.sh
./scripts/roll-slice-ports.sh 1 2 3 4
```

Requires SSH as `admin@streamrtnN` with key auth.

## Promote to docker-slice-pi

From the monitoring-nia-pi repo root:

```bash
rsync -a --delete \
  --exclude '.env' \
  template/endpoint/ \
  ../docker-slice-pi/
```

Review the diff in `docker-slice-pi`, then deploy on each Pi. Do not commit
secrets. Full MkDocs stays in this repo — the slice README only points here.
