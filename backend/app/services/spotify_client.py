from typing import Any, List, Optional

import httpx
from app.utils.logger import logger


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
    async def _put(cls, url: str, token: str, payload: Any = None) -> bool:
        """
        Internal helper for PUT requests (e.g. playback controls).
        """
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(url, headers=headers, json=payload)
                if response.status_code in (200, 204):
                    return True
                else:
                    logger.error(
                        f"Spotify API PUT Error [{response.status_code}]: {response.text}"
                    )
                    return False
            except Exception as e:
                logger.error(f"HTTP Request Failed: {e}")
                return False

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

    @classmethod
    async def get_request(cls, url: str, token: str) -> Optional[Any]:
        """
        Public wrapper for GET requests.
        """
        return await cls._get(url, token)

    @classmethod
    async def get_audio_features(cls, token: str, track_ids: List[str]) -> List[dict]:
        """
        Fetch audio features for a list of track IDs.
        """
        if not track_ids:
            return []

        ids_param = ",".join(track_ids)
        url = f"{cls.BASE_URL}/audio-features?ids={ids_param}"
        data = await cls._get(url, token)
        return data.get("audio_features", []) if data else []
