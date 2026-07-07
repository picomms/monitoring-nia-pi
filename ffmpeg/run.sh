#!/bin/sh

set -eu

INTERVAL="${POLL_INTERVAL:-60}"

while true
do
    START=$(date +%s)

    python /app/monitor.py || true

    END=$(date +%s)

    ELAPSED=$((END - START))

    if [ "$ELAPSED" -lt "$INTERVAL" ]; then
        sleep $((INTERVAL - ELAPSED))
    fi
done
