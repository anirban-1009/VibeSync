from typing import Any, Dict, List

from app.services.spotify_client import SpotifyService
from app.utils.models import Track


async def get_recommendations(
    token: str,
    seeds: Dict[str, List[str]],
    history: List[Track],
    targets: Dict[str, Any],
) -> List[dict]:
    """
    Get recommendations based on seeds and adjusted by history vibe.
    Returns a list of raw track dictionaries from Spotify API.
    """

    query_params = {**targets, "limit": 10}

    for key in ["seed_tracks", "seed_artists", "seed_genres"]:
        if key in seeds and seeds[key]:
            query_params[key] = ",".join(seeds[key][:5])

    query_str = "&".join([f"{k}={v}" for k, v in query_params.items()])
    url = f"{SpotifyService.BASE_URL}/recommendations?{query_str}"

    data = await SpotifyService.get_request(url, token)

    if data and "tracks" in data:
        return data["tracks"]

    return []
