#!/usr/bin/env python3

import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from fractions import Fraction
from pathlib import Path

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv

from vimeo import VimeoClient


# -----------------------------------------------------------------------------
# Environment
# -----------------------------------------------------------------------------

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

VIMEO_EVENTID = os.getenv("VIMEO_EVENTID")
INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_ADMIN_TOKEN", "change-me")
INFLUX_ORG = os.getenv("INFLUX_ORG", "default")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "default")

DEVICE_NAME = os.getenv("DEVICE_NAME", "encoder01")


# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("vimeo-exporter")


# -----------------------------------------------------------------------------
# Metrics model
# -----------------------------------------------------------------------------

@dataclass
class StreamMetrics:
    device: str = DEVICE_NAME

    # API
    api_ok: bool = False
    api_ms: float = 0.0

    # Probe
    probe_ok: bool = False
    probe_ms: float = 0.0

    # Stream identity
    width: int = 0
    height: int = 0
    fps: float = 0.0
    bitrate: int = 0
    codec: str = "unknown"
    audio_codec: str = "unknown"
    audio_channels: int = 0
    duration: float = 0.0

    # Health
    healthy: bool = False
    failure_reason: str = ""


# -----------------------------------------------------------------------------
# InfluxDB
# -----------------------------------------------------------------------------

influx = influxdb_client.InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG,
)

write_api = influx.write_api(write_options=SYNCHRONOUS)


def publish(metrics: StreamMetrics):
    point = influxdb_client.Point("stream").tag("device", metrics.device)

    for k, v in asdict(metrics).items():
        if isinstance(v, (str, bool, int, float)):
            point.field(k, v)

    write_api.write(
        bucket=INFLUX_BUCKET,
        org=INFLUX_ORG,
        record=point,
    )


# -----------------------------------------------------------------------------
# Vimeo client
# -----------------------------------------------------------------------------

client = VimeoClient(
    token=require_env("VIMEO_TOKEN"),
    key=require_env("VIMEO_KEY"),
    secret=require_env("VIMEO_SECRET"),
    eventid=VIMEO_EVENTID,
)


def get_hls_url(metrics: StreamMetrics):
    start = time.monotonic()

    url = f"https://api.vimeo.com/me/live_events/{VIMEO_EVENTID}/m3u8_playback"
    response = client.get(url)

    metrics.api_ms = (time.monotonic() - start) * 1000

    if response.status_code != 200:
        metrics.api_ok = False
        metrics.failure_reason = f"vimeo_api_{response.status_code}"
        return None

    data = response.json()
    hls = data.get("m3u8_playback_url")

    if not hls:
        metrics.api_ok = False
        metrics.failure_reason = "missing_hls_url"
        return None

    metrics.api_ok = True
    return hls


# -----------------------------------------------------------------------------
# ffprobe
# -----------------------------------------------------------------------------

def probe_stream(hls_url: str, metrics: StreamMetrics):
    start = time.monotonic()

    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-print_format",
                "json",
                "-show_streams",
                "-show_format",
                hls_url,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        metrics.probe_ms = (time.monotonic() - start) * 1000
        metrics.probe_ok = True

        data = json.loads(result.stdout)

    except subprocess.CalledProcessError:
        metrics.probe_ms = (time.monotonic() - start) * 1000
        metrics.probe_ok = False
        metrics.failure_reason = "ffprobe_failed"
        return None

    except json.JSONDecodeError:
        metrics.probe_ms = (time.monotonic() - start) * 1000
        metrics.probe_ok = False
        metrics.failure_reason = "ffprobe_json_error"
        return None

    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    audio = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)

    if not video:
        metrics.probe_ok = False
        metrics.failure_reason = "no_video_stream"
        return None

    metrics.width = video.get("width", 0)
    metrics.height = video.get("height", 0)

    try:
        metrics.fps = float(Fraction(video.get("avg_frame_rate", "0/1")))
    except Exception:
        metrics.fps = 0.0

    try:
        metrics.bitrate = int(video.get("bit_rate", 0))
    except Exception:
        metrics.bitrate = 0

    metrics.codec = video.get("codec_name", "unknown")

    if audio:
        metrics.audio_codec = audio.get("codec_name", "unknown")
        metrics.audio_channels = audio.get("channels", 0)

    try:
        metrics.duration = float(data.get("format", {}).get("duration", 0))
    except Exception:
        metrics.duration = 0.0

    return data


# -----------------------------------------------------------------------------
# Health evaluation
# -----------------------------------------------------------------------------

def evaluate_health(metrics: StreamMetrics):
    if not metrics.api_ok:
        return False

    if not metrics.probe_ok:
        return False

    if metrics.width == 0 or metrics.height == 0:
        metrics.failure_reason = "invalid_resolution"
        return False

    if metrics.fps == 0:
        metrics.failure_reason = "invalid_fps"
        return False

    if metrics.bitrate == 0:
        metrics.failure_reason = "invalid_bitrate"
        return False

    return True


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    metrics = StreamMetrics()

    try:
        hls_url = get_hls_url(metrics)

        if not hls_url:
            metrics.healthy = False
            publish(metrics)
            return 0

        probe_stream(hls_url, metrics)

        metrics.healthy = evaluate_health(metrics)

        publish(metrics)

        logger.info(f"Healthy: {metrics.healthy}")

        return 0

    except Exception as e:
        metrics.healthy = False
        metrics.failure_reason = f"unexpected_error:{str(e)}"

        publish(metrics)

        logger.exception("Unhandled error in exporter")

        return 1


if __name__ == "__main__":
    sys.exit(main())
