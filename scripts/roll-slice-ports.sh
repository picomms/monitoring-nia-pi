#!/usr/bin/env bash
# Copy published-port slice compose to streamrtn hosts and recreate exporters.
# Usage: ./scripts/roll-slice-ports.sh [1 2 3 4]
set -euo pipefail
cd "$(dirname "$0")/.."
SRC="${SLICE_SRC:-../docker-slice-pi}"
hosts=("${@:-1 2 3 4}")
# shellcheck disable=SC2206
nums=($hosts)

for n in "${nums[@]}"; do
  host="admin@streamrtn${n}"
  echo "======== streamrtn${n} ========"
  scp -o BatchMode=yes \
    "$SRC/compose.yml" "$SRC/justfile" "$SRC/env.sample" "$SRC/README.md" \
    "$host:/home/admin/code/docker-slice-pi/"
  scp -o BatchMode=yes \
    "$SRC/blackbox/blackbox.yml" \
    "$host:/home/admin/code/docker-slice-pi/blackbox/blackbox.yml"
  ssh -o BatchMode=yes "$host" \
    'cd /home/admin/code/docker-slice-pi && (command -v just >/dev/null && just up || docker compose up -d) && curl -sS -o /dev/null -w "node=%{http_code} bb=" http://127.0.0.1:9100/metrics && curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:9115/metrics'
done
