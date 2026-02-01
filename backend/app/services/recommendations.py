import urllib.parse
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
    Get recommendations using SEARCH API (fallback mode only).
    Bypasses restricted /recommendations endpoint.
    """
    import random

    from app.utils.logger import logger

    # 1. Determine Search Strategy
    # Priority: Genre -> Artist -> Track's Artist -> Default

    query = ""

    candidate_genres = []
    if seeds.get("seed_genres"):
        candidate_genres.extend(seeds["seed_genres"])
    elif targets.get("seed_genres"):
        pass

    if candidate_genres:
        chosen_genre = random.choice(candidate_genres)
        query = f'genre:"{chosen_genre}"'
        logger.debug(f"Search Strategy: Genre ({chosen_genre})")

    if not query:
        seed_artist_id = (
            seeds.get("seed_artists", [])[0] if seeds.get("seed_artists") else None
        )

        # If no explicit artist seed, check seed_tracks to find the artist
        if not seed_artist_id and seeds.get("seed_tracks"):
            track_id = seeds["seed_tracks"][0]

            track_data = await SpotifyService.get_request(
                f"{SpotifyService.BASE_URL}/tracks/{track_id}", token
            )
            if track_data and "artists" in track_data:
                artist_name = track_data["artists"][0]["name"]
                # To prevent funneling, we ideally want 'Related' but we can't.
                # So we search for the artist directly.
                # To mitigate funneling, we depend on OFFSET randomization.
                query = f'artist:"{artist_name}"'
                logger.debug(f"Search Strategy: Artist ({artist_name})")

    if not query:
        query = "genre:pop"
        logger.debug("Search Strategy: Default (Pop)")

    # 2. Perform Search with Randomization

    try:
        # Getting a random offset is KEY to variety
        offset = random.randint(0, 100)

        encoded_query = urllib.parse.quote(query)
        url = f"{SpotifyService.BASE_URL}/search?q={encoded_query}&type=track&limit=20&offset={offset}&market=from_token"

        data = await SpotifyService.get_request(url, token)

        if data and "tracks" in data and data["tracks"]["items"]:
            tracks = data["tracks"]["items"]
            random.shuffle(tracks)
            return tracks

        # If offset was too high and returned nothing, try offset 0
        if offset > 0:
            url_retry = f"{SpotifyService.BASE_URL}/search?q={encoded_query}&type=track&limit=20&offset=0&market=from_token"
            data_retry = await SpotifyService.get_request(url_retry, token)
            if data_retry and "tracks" in data_retry:
                return data_retry["tracks"]["items"]

    except Exception as e:
        logger.error(f"Search fallback failed: {e}")

    return []
