# NIA Monitoring — endpoint stack

Reusable Compose template for Raspberry Pi exporters. One shared repo
([`docker-slice-pi`](https://github.com/picomms/docker-slice-pi)); unique `.env`
per host.

**Documentation (source of truth)** lives in the server repo:

- [Slice template](https://picomms.github.io/monitoring-nia-pi/developer/slice/)
- [Cloudflare hostname / tunnel guide](https://picomms.github.io/monitoring-nia-pi/cloudflare/)

## Quick start

```bash
cp env.sample .env
# set HOST_ID and TUNNEL_TOKEN
just up
just ps
```

Then in Cloudflare Zero Trust, add Public Hostnames on this host's tunnel:

| Hostname | URL |
| --- | --- |
| `mon-node-<HOST_ID>.cothrom.ie` | `http://node_exporter:9100` |
| `mon-blackbox-<HOST_ID>.cothrom.ie` | `http://blackbox_exporter:9115` |

Protect both with Cloudflare Access (do not leave `/metrics` world-readable).

## Verify locally

```bash
docker compose exec -T node_exporter wget -qO- http://127.0.0.1:9100/metrics | head
docker compose exec -T blackbox_exporter wget -qO- http://127.0.0.1:9115/metrics | head
```

Frontend reachability (what `cloudflared` needs — the image has no shell/`wget`):

```bash
NET=$(docker compose config --format json | python3 -c "import sys,json; print(json.load(sys.stdin)['networks']['frontend']['name'])")
docker run --rm --network "$NET" curlimages/curl:8.5.0 -sf -o /dev/null -w '%{http_code}\n' http://node_exporter:9100/metrics
docker run --rm --network "$NET" curlimages/curl:8.5.0 -sf -o /dev/null -w '%{http_code}\n' http://blackbox_exporter:9115/metrics
```

Cherry Prometheus scrapes arrive in milestone M4 — this stack only exposes exporters.
