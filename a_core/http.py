from asyncio.log import logger
from httpx import AsyncClient
from functools import lru_cache

import httpx
local = False

local_path = "http://host.lima.internal:8000/api/v1/"
remote_path = "https://dev.keeplist.io/api/v1/"
path = local_path if local else remote_path

@lru_cache()
def get_http_client():
    return AsyncClient(timeout=30.0, limits=httpx.Limits(max_keepalive_connections=5))

async def get_api_results(url_ending, params=None):
    client = get_http_client()
    if (not url_ending.endswith('/')) and not "?" in url_ending:
        url_ending = url_ending + '/'
    try:
        response = await client.get(f"{path}{url_ending}", params=params)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        # Handle HTTP errors
        logger.error(f"HTTP error occurred: {e}")
        return {}
    except Exception as e:
        # Handle other errors
        logger.error(f"Error occurred: {e}")
        return {}