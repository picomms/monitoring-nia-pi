# Cloudflare

This is the thin operator guide for the monitoring link. It covers the
Cloudflare Tunnel and Access pattern we need for Cherry Grafana now, and the
hostname contract that the Raspberry Pi exporter stack will follow later.

Full Zero Trust administration is intentionally out of scope. This page is only
the project-specific runbook for `cothrom.ie`.

## Naming

Monitoring hostnames are **single-label** names under the apex (`*.cothrom.ie`)
with a `mon-` prefix. That keeps them distinct from other services on the zone
and stays inside Cloudflare Universal SSL coverage.

!!! warning "Do not use nested names like `grafana.mon.cothrom.ie`"
    Universal SSL covers `cothrom.ie` and `*.cothrom.ie` only — not
    `*.mon.cothrom.ie`. Nested hostnames produce
    `ERR_SSL_VERSION_OR_CIPHER_MISMATCH` until Advanced Certificate Manager
    covers them. Prefer `mon-grafana.cothrom.ie`.

| Role | Hostname | Tunnel ingress target |
| --- | --- | --- |
| Cherry Grafana | `mon-grafana.cothrom.ie` | `http://grafana:3000` |
| Host node metrics | `mon-node-<HOST_ID>.cothrom.ie` | `http://node_exporter:9100` |
| Host blackbox metrics | `mon-blackbox-<HOST_ID>.cothrom.ie` | `http://blackbox_exporter:9115` |

Use one hostname per exporter. Avoid path-based routing; it would require an
extra path-aware proxy and would make the endpoint stack less reusable.

## Stack contract

Every host runs the same Compose shape:

- `cloudflared` on `frontend` only
- tunnel-facing services on `frontend`
- internal services on `backend`
- host-specific names and tokens in `.env`

Per-host variables:

| Variable | Example | Purpose |
| --- | --- | --- |
| `HOST_ID` | `cherry`, `pi1` | Slug used when creating DNS / Public Hostname rows |
| `TUNNEL_TOKEN` | secret | Token for that host's remotely managed tunnel |
| `GRAFANA_ROOT_URL` | `https://mon-grafana.cothrom.ie` | Grafana's externally visible URL |

One remotely managed tunnel per host. Ingress routes are configured in
Cloudflare Zero Trust; Compose only runs `cloudflared tunnel run` with the token.

## Cherry Grafana

### 1. Create the tunnel

In Cloudflare Zero Trust:

1. Open **Networks → Tunnels**.
2. Create a Cloudflare Tunnel named `monitoring-nia-cherry`.
3. Choose Docker as the connector type.
4. Copy the generated token into Cherry's `.env`:

```dotenv
HOST_ID=cherry
TUNNEL_TOKEN=...
GRAFANA_ROOT_URL=https://mon-grafana.cothrom.ie
```

Do not commit `.env`.

### 2. Add the public hostname

On the `monitoring-nia-cherry` tunnel, add:

| Field | Value |
| --- | --- |
| Subdomain | `mon-grafana` |
| Domain | `cothrom.ie` |
| Type | `HTTP` |
| URL | `grafana:3000` |

Cloudflare will create the DNS route for `mon-grafana.cothrom.ie` to the tunnel.
Keep the record **proxied** (orange cloud).

If you previously created `grafana.mon.cothrom.ie`, delete that Public Hostname
and its DNS record to avoid leftover TLS failures.

### 3. Protect Grafana with Access

Create a Cloudflare Access application:

| Field | Value |
| --- | --- |
| Application type | Self-hosted |
| Application domain | `mon-grafana.cothrom.ie` |
| Session duration | Use the existing Cothrom/Picomms policy default |

Add the existing human access policy for operators. Grafana is intentionally the
only monitoring hostname intended for browser access at M2.

### 4. Start the connector

```bash
just up-tunnel
```

Verify:

```bash
just ps
just logs cloudflared
```

Then open `https://mon-grafana.cothrom.ie`. You should see a Cloudflare Access
challenge before Grafana. Local break-glass access remains available at
`http://localhost:3000` while the port is published.

## Endpoint tunnel (slice / RPi)

The reusable endpoint stack is documented in [Slice](developer/slice.md). Compose
lives in `template/endpoint/` (canonical) and is copied to `docker-slice-pi` for
deploy. M4 wires Cherry Prometheus scrapes; M3 only publishes the hostnames.

For a host with:

```dotenv
HOST_ID=pi1
TUNNEL_TOKEN=...
```

1. Create a remotely managed tunnel named `monitoring-slice-pi1`.
2. Put the token in that Pi's `.env`.
3. Add Public Hostnames on that tunnel:

| Hostname | Target |
| --- | --- |
| `mon-node-pi1.cothrom.ie` | `http://node_exporter:9100` |
| `mon-blackbox-pi1.cothrom.ie` | `http://blackbox_exporter:9115` |

4. Create Cloudflare Access applications for both hostnames. Exporter endpoints
   serve unauthenticated `/metrics` locally — do not leave them world-readable.
5. Start the stack with `just up` and confirm the connector is healthy.

## Prometheus scrape authentication

Remote exporter hostnames should be protected by Cloudflare Access. For
machine-to-machine scraping, create an Access Service Token and attach a policy
that allows that token to the exporter applications.

Prometheus will later send:

```yaml
headers:
  CF-Access-Client-Id: <client id>
  CF-Access-Client-Secret: <client secret>
```

Do not add these headers or remote scrape jobs in M2; that belongs to M4. This
section documents the shape so the Access applications are created correctly.

## Coexisting with other services

`cothrom.ie` already has other services. Keep monitoring isolated:

- Use `mon-*` hostnames for monitoring only.
- Do not reuse the `docker-cherry-pi` tunnel or its bare `frontend` network.
- Do not move this stack into `docker-cherry-pi`; NIA monitoring remains in this
  repository.
- Do not expose exporter hostnames without Access, even if they are hard to
  guess.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `ERR_SSL_VERSION_OR_CIPHER_MISMATCH` | Nested name like `*.mon.cothrom.ie` lacks a Universal SSL cert — switch to `mon-*.cothrom.ie` |
| `just up-tunnel` exits immediately | `TUNNEL_TOKEN` is missing or invalid in `.env` |
| Cloudflare shows connector offline | `just logs cloudflared`; confirm the token belongs to `monitoring-nia-cherry` |
| 502 from Cloudflare | Public Hostname target should be `http://grafana:3000`, not `https://...` or `localhost:3000` |
| Grafana redirects to localhost | Set `GRAFANA_ROOT_URL=https://mon-grafana.cothrom.ie` and recreate Grafana |
| Access challenge missing | Confirm the Access application domain exactly matches `mon-grafana.cothrom.ie` |
| HTTP works, HTTPS fails | Tunnel/DNS is fine but TLS certificate coverage isn’t — see SSL warning above |

## Done criteria for M2

- `docs/cloudflare.md` explains tunnel, DNS, Access, and `.env` setup without
  requiring repo-specific guessing.
- `mon-grafana.cothrom.ie` routes through this repo's `cloudflared` service.
- Grafana is protected by Cloudflare Access.
