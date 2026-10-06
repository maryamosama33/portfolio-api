import logging
import os

import httpx

logger = logging.getLogger(__name__)

# Includes the version prefix, e.g. http://api:8000/api/v1
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/api/v1")
TIMEOUT_SECONDS = 15


async def get_json(endpoint: str, params: dict | None = None) -> dict | None:
    """GET an API endpoint. Returns None on any failure so tools can degrade gracefully."""
    try:
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        logger.warning("Portfolio API call %s failed: %s", endpoint, exc)
        return None
