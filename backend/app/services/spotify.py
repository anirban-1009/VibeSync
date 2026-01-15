import logging

import httpx

logger = logging.getLogger(__name__)


async def fetch_user_top_items(token: str, type: str = "tracks", limit: int = 20):
    """
    Fetch a user's top items (tracks or artists) from Spotify.
    """
    url = f"https://api.spotify.com/v1/me/top/{type}?limit={limit}"
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get("items", [])
            else:
                logger.error(
                    f"Failed to fetch {type}: {response.status_code} {response.text}"
                )
                return []
        except Exception as e:
            logger.error(f"Error fetching {type}: {e}")
            return []
