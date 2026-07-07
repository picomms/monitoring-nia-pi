#!/usr/bin/env python3

import json
import logging
import os
import sys

from vimeo import VimeoClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def require_env(name):
    value = os.environ.get(name)
    if not value:
        logger.error(f"Required environment variable {name} is not set")
        sys.exit(1)
    return value


try:
    event_id = require_env("VIMEO_EVENTID")

    client = VimeoClient(
        token=require_env("VIMEO_TOKEN"),
        key=require_env("VIMEO_KEY"),
        secret=require_env("VIMEO_SECRET"),
    )

    # Test API URL
    test_url = f"https://api.vimeo.com/live_events/{event_id}/export_vpaas_analytics"

    # Perform HTTP POST request (Vimeo's export endpoint only allows POST/OPTIONS)
    logger.info(f"Fetching data from: {test_url}")
    response = client.post(test_url)

    if response.status_code != 200:
        logger.error(
            f"API request failed with status code {response.status_code}: {response.text}"
        )
        sys.exit(1)

    # Print the JSON response
    print(json.dumps(response.json(), indent=2))

except json.JSONDecodeError as e:
    logger.error(f"Failed to parse JSON response: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    sys.exit(1)
