import random
from abc import ABC, abstractmethod
from typing import Dict

from app.services.spotify_client import SpotifyService
from app.utils.logger import logger


class StrategyContext:
    def __init__(self, seeds: Dict, token: str):
        self.seeds = seeds
        self.token = token
        self.queries = []
        self.seed_artist_id = None
        self.seed_artist_name = None

    def add_query(self, query: str):
        if query and query not in self.queries:
            self.queries.append(query)

    async def resolve_seed_artist(self):
        if self.seed_artist_id:
            return

        # Check explicit seed
        if self.seeds.get("seed_artists"):
            self.seed_artist_id = self.seeds["seed_artists"][0]

        # Or resolve from track
        if not self.seed_artist_id and self.seeds.get("seed_tracks"):
            try:
                track_id = self.seeds["seed_tracks"][0]
                track_data = await SpotifyService.get_request(
                    f"{SpotifyService.BASE_URL}/tracks/{track_id}", self.token
                )
                if track_data and "artists" in track_data:
                    self.seed_artist_id = track_data["artists"][0]["id"]
                    self.seed_artist_name = track_data["artists"][0]["name"]
            except Exception as e:
                logger.warning(f"Failed to resolve seed artist: {e}")


class RecommendationStrategy(ABC):
    @abstractmethod
    async def execute(self, ctx: StrategyContext):
        pass


class GenreSeedStrategy(RecommendationStrategy):
    async def execute(self, ctx: StrategyContext):
        genres = ctx.seeds.get("seed_genres", [])
        if genres:
            chosen = random.choice(genres)
            ctx.add_query(f'genre:"{chosen}"')
            logger.debug(f"Strategy: Genre Seed ({chosen})")


class ArtistDerivedGenreStrategy(RecommendationStrategy):
    async def execute(self, ctx: StrategyContext):
        await ctx.resolve_seed_artist()
        if not ctx.seed_artist_id:
            return

        try:
            artist_data = await SpotifyService.get_request(
                f"{SpotifyService.BASE_URL}/artists/{ctx.seed_artist_id}", ctx.token
            )
            if artist_data:
                ctx.seed_artist_name = artist_data.get("name")  # Update name if missing
                genres = artist_data.get("genres", [])

                if genres:
                    chosen_genres = random.sample(genres, min(2, len(genres)))
                    for g in chosen_genres:
                        ctx.add_query(f'genre:"{g}"')
                        logger.debug(f"Strategy: Derived Genre ({g})")
        except Exception:
            pass


class RelatedArtistStrategy(RecommendationStrategy):
    async def execute(self, ctx: StrategyContext):
        # Only run if we need more variety
        if len(ctx.queries) >= 2:
            return

        await ctx.resolve_seed_artist()
        if not ctx.seed_artist_id:
            return

        try:
            related_data = await SpotifyService.get_request(
                f"{SpotifyService.BASE_URL}/artists/{ctx.seed_artist_id}/related-artists",
                ctx.token,
                allow_404=True,
            )

            if related_data and "artists" in related_data:
                related_list = related_data["artists"]
                candidates = [a for a in related_list if a["id"] != ctx.seed_artist_id]

                if candidates:
                    chosen = random.choice(candidates)
                    ctx.add_query(f'artist:"{chosen["name"]}"')
                    logger.debug(f"Strategy: Related Artist ({chosen['name']})")
        except Exception:
            pass


class SeedArtistFallbackStrategy(RecommendationStrategy):
    async def execute(self, ctx: StrategyContext):
        # Last resort if no other queries exist
        if ctx.queries:
            return

        await ctx.resolve_seed_artist()
        if ctx.seed_artist_name:
            ctx.add_query(f'artist:"{ctx.seed_artist_name}"')
            logger.debug(f"Strategy: Seed Artist Fallback ({ctx.seed_artist_name})")


class DefaultFallbackStrategy(RecommendationStrategy):
    async def execute(self, ctx: StrategyContext):
        if not ctx.queries:
            ctx.add_query("genre:pop")
            logger.debug("Strategy: Default Fallback (Pop)")
