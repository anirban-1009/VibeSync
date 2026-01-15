from typing import Any, List, Optional

import httpx
from app.services.logger import get_logger

logger = get_logger(__name__)


class SpotifyService:
    """
    Service class to interact with the Spotify Web API.
    Handles user data fetching, recommendations, and playback controls.
    """

    BASE_URL = "https://api.spotify.com/v1"

    @classmethod
    async def _get(cls, url: str, token: str) -> Optional[Any]:
        """
        Internal helper for GET requests with error handling.
        """
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(
                        f"Spotify API Error [{response.status_code}]: {response.text}"
                    )
                    return None
            except Exception as e:
                logger.error(f"HTTP Request Failed: {e}")
                return None

    @classmethod
    async def fetch_user_top_items(
        cls, token: str, type: str = "tracks", limit: int = 20
    ) -> List[dict]:
        """
        Fetch a user's top items (tracks or artists) from Spotify.
        """
        url = f"{cls.BASE_URL}/me/top/{type}?limit={limit}"
        data = await cls._get(url, token)
        return data.get("items", []) if data else []
