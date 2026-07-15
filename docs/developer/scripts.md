# Scripts

Operational helpers under `scripts/`. They are not long-running services and are
not started by Compose.

## `scripts/roll-slice-ports.sh`

Rolls the endpoint template port-publishing changes across several slice Pis from
Cherry. It assumes SSH key access as `admin@streamrtnN`.

```bash
chmod +x scripts/roll-slice-ports.sh
./scripts/roll-slice-ports.sh 1 2 3 4
```

Review the script before running it against hosts. It copies the deploy files to
`docker-slice-pi` on each Pi and restarts the slice stack with `just up`.
