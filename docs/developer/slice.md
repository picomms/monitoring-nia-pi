# Slice template

The endpoint stack for Raspberry Pis. One shared deploy repo
([`docker-slice-pi`](https://github.com/picomms/docker-slice-pi)); unique `.env`
per host. This page is the operator contract.

The server stack (Prometheus / Grafana) stays in this repository on Cherry. The
slice stack only exposes exporters for Cherry to scrape later (M4).

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
| `compose.yml` | `cloudflared`, `node_exporter`, `blackbox_exporter` |
| `env.sample` | `HOST_ID`, `TUNNEL_TOKEN`, image pins |
| `blackbox/blackbox.yml` | Probe modules (`http_2xx`, `icmp`, `tcp_connect`) — no targets |
| `justfile` | `up` / `down` / `ps` / `logs` / `config` |
| `README.md` | Quick start + link back to these docs |

## Env contract

| Variable | Example | Purpose |
| --- | --- | --- |
| `HOST_ID` | `pi1` | Slug for DNS / Public Hostname rows |
| `TUNNEL_TOKEN` | secret | Remotely managed tunnel token for this Pi |
| `CLOUDFLARED_VERSION` | `2026.7.1` | Image pin |
| `NODE_EXPORTER_VERSION` | `v1.12.0` | Image pin |
| `BLACKBOX_EXPORTER_VERSION` | `v0.28.0` | Image pin |

Compose layout is identical on every Pi. Do not branch YAML per host — put
differences in `.env` only.

## Hostnames

See [Cloudflare](../cloudflare.md) for tunnel and Access setup. Endpoint names:

| Role | Hostname | Ingress target |
| --- | --- | --- |
| Node | `mon-node-<HOST_ID>.cothrom.ie` | `http://node_exporter:9100` |
| Blackbox | `mon-blackbox-<HOST_ID>.cothrom.ie` | `http://blackbox_exporter:9115` |

Tunnel name convention: `monitoring-slice-<HOST_ID>`.

## Networks

Project-scoped `frontend` and `backend` only. Do **not** pin bare external names
like `name: frontend` — that collides with other Compose stacks on a host.

| Service | Network | Notes |
| --- | --- | --- |
| `cloudflared` | `frontend` | Publishes Public Hostnames |
| `node_exporter` | `frontend` | Reachable by cloudflared as `node_exporter:9100` |
| `blackbox_exporter` | `frontend` | Reachable by cloudflared as `blackbox_exporter:9115` |

No host `ports:` — publish only via Cloudflare. Debug with `docker compose exec`.

## Bring-up

```bash
cp env.sample .env
# set HOST_ID and TUNNEL_TOKEN
just up
just ps
just logs cloudflared
```

### Local metrics check

```bash
docker compose exec -T node_exporter wget -qO- http://127.0.0.1:9100/metrics | head
docker compose exec -T blackbox_exporter wget -qO- http://127.0.0.1:9115/metrics | head
```

### Frontend reachability (what the tunnel needs)

The `cloudflared` image has no shell/`wget`. Probe from any container on the
project `frontend` network (same place the tunnel connector sits):

```bash
NET=$(docker compose config --format json | python3 -c "import sys,json; print(json.load(sys.stdin)['networks']['frontend']['name'])")
docker run --rm --network "$NET" curlimages/curl:8.5.0 -sf -o /dev/null -w '%{http_code}\n' http://node_exporter:9100/metrics
docker run --rm --network "$NET" curlimages/curl:8.5.0 -sf -o /dev/null -w '%{http_code}\n' http://blackbox_exporter:9115/metrics
```

Both should print `200`.

### Cloudflare checklist (pilot Pi)

1. Create remotely managed tunnel `monitoring-slice-<HOST_ID>`.
2. Put the token in `.env` as `TUNNEL_TOKEN`.
3. Public Hostname `mon-node-<HOST_ID>.cothrom.ie` → `http://node_exporter:9100`.
4. Public Hostname `mon-blackbox-<HOST_ID>.cothrom.ie` → `http://blackbox_exporter:9115`.
5. Cloudflare Access applications on both hostnames (not world-readable).
6. Confirm connector healthy in Zero Trust and in `just logs cloudflared`.

## M3 vs M4

| Milestone | This stack | Cherry |
| --- | --- | --- |
| **M3** | Exporters up; tunnel hostnames published | Does not scrape yet |
| **M4** | Unchanged | Static scrape jobs + Access service token + dashboard panels |

**M3 verification (2026-07-14):** on Cherry, `docker compose up -d node_exporter
blackbox_exporter` from the promoted `docker-slice-pi` copy — both exporters
healthy, no published host ports, HTTP 200 to `/metrics` from a peer container on
`slice-pi_frontend` (same network as `cloudflared`). Create
`monitoring-slice-<HOST_ID>` + Public Hostnames when the pilot Pi has a real
`TUNNEL_TOKEN`.

## Promote to docker-slice-pi

From the monitoring-nia-pi repo root:

```bash
rsync -a --delete \
  --exclude '.env' \
  template/endpoint/ \
  ../docker-slice-pi/
```

Review the diff in `docker-slice-pi`, then deploy on the pilot Pi. Do not commit
secrets. Full MkDocs stays in this repo — the slice README only points here.
