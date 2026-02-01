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
    import asyncio
    import random

    from app.services.recommendation_strategies import (
        ArtistDerivedGenreStrategy,
        DefaultFallbackStrategy,
        GenreSeedStrategy,
        RelatedArtistStrategy,
        SeedArtistFallbackStrategy,
        StrategyContext,
    )
    from app.utils.logger import logger

    # 1. Initialize Context
    ctx = StrategyContext(seeds, token)

    # 2. Define Strategy Pipeline
    strategies = [
        GenreSeedStrategy(),
        ArtistDerivedGenreStrategy(),
        RelatedArtistStrategy(),
        SeedArtistFallbackStrategy(),
        DefaultFallbackStrategy(),
    ]

    # 3. Execute Strategies Sequentially
    for strategy in strategies:
        try:
            await strategy.execute(ctx)
        except Exception as e:
            logger.error(f"Strategy {strategy.__class__.__name__} failed: {e}")

    # 4. Prepare Parallel Search Tasks
    queries = ctx.queries
    # Only keep unique queries to avoid duplicate work
    unique_queries = list(set(queries))
    # Limit max queries to 3 to prevent rate limits
    if len(unique_queries) > 3:
        unique_queries = random.sample(unique_queries, 3)

    async def fetch_search_results(q: str, limit: int = 10) -> List[dict]:
        try:
            # Random offset for variety
            offset = random.randint(0, 50)
            encoded_q = urllib.parse.quote(q)
            url = f"{SpotifyService.BASE_URL}/search?q={encoded_q}&type=track&limit={limit}&offset={offset}&market=from_token"

            data = await SpotifyService.get_request(url, token, allow_404=True)
            if data and "tracks" in data and data["tracks"]["items"]:
                return data["tracks"]["items"]

            # Retry with offset 0 if failed
            if offset > 0:
                url0 = f"{SpotifyService.BASE_URL}/search?q={encoded_q}&type=track&limit={limit}&offset=0&market=from_token"
                data0 = await SpotifyService.get_request(url0, token, allow_404=True)
                if data0 and "tracks" in data0:
                    return data0["tracks"]["items"]

            return []
        except Exception as err:
            logger.error(f"Search query '{q}' failed: {err}")
            return []

    tasks = [fetch_search_results(q) for q in unique_queries]

    try:
        results_lists = await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Async gathering of recommendations failed: {e}")
        return []

    # 3. Aggregate and Shuffle
    all_tracks = []
    seen_ids = set()

    for r_list in results_lists:
        for t in r_list:
            if t["id"] not in seen_ids:
                all_tracks.append(t)
                seen_ids.add(t["id"])

    random.shuffle(all_tracks)

    # Return top 20
    return all_tracks[:20]
