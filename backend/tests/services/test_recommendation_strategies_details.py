from unittest.mock import AsyncMock, patch

import pytest
from app.services.recommendation_strategies import (
    ArtistDerivedGenreStrategy,
    DefaultFallbackStrategy,
    GenreSeedStrategy,
    RelatedArtistStrategy,
    SeedArtistFallbackStrategy,
    StrategyContext,
)


@pytest.mark.asyncio
async def test_genre_seed_strategy():
    ctx = StrategyContext(seeds={"seed_genres": ["rock"]}, token="tok")
    strategy = GenreSeedStrategy()
    await strategy.execute(ctx)
    assert 'genre:"rock"' in ctx.queries

    # Test empty genres
    ctx2 = StrategyContext(seeds={}, token="tok")
    await strategy.execute(ctx2)
    assert len(ctx2.queries) == 0


@patch("app.services.spotify_client.SpotifyService.get_request", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_artist_derived_strategy(mock_get):
    # Case 1: Resolves seed artist from track
    ctx = StrategyContext(seeds={"seed_tracks": ["t1"]}, token="tok")
    strategy = ArtistDerivedGenreStrategy()

    # Mocks
    # 1. resolve_seed_artist -> gets track t1 -> artist a1
    # 2. execute -> gets artist a1 -> genres ["pop", "rock"]
    mock_get.side_effect = [
        {"artists": [{"id": "a1", "name": "A1"}]},  # track response
        {"name": "A1", "genres": ["pop", "rock"]},  # artist response
    ]

    await strategy.execute(ctx)

    assert ctx.seed_artist_id == "a1"
    assert 'genre:"pop"' in ctx.queries or 'genre:"rock"' in ctx.queries
    # Verify we limited to 2
    count = sum(1 for q in ctx.queries if "genre:" in q)
    assert 0 < count <= 2


@patch("app.services.spotify_client.SpotifyService.get_request", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_related_artist_strategy(mock_get):
    ctx = StrategyContext(seeds={"seed_artists": ["a1"]}, token="tok")
    strategy = RelatedArtistStrategy()

    # Mock related artists response
    mock_get.return_value = {
        "artists": [
            {"id": "a2", "name": "A2"},
            {"id": "a3", "name": "A3"},
        ]
    }

    await strategy.execute(ctx)

    assert ctx.seed_artist_id == "a1"  # Already set in seeds
    # Should pick one related artist
    assert any('artist:"A2"' in q or 'artist:"A3"' in q for q in ctx.queries)

    # Test skipping if query buffer full
    ctx.queries = ["q1", "q2"]
    mock_get.reset_mock()
    await strategy.execute(ctx)
    mock_get.assert_not_called()


@patch("app.services.spotify_client.SpotifyService.get_request", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_seed_artist_fallback(mock_get):
    ctx = StrategyContext(seeds={"seed_artists": ["a1"]}, token="tok")
    # Need name for fallback
    ctx.seed_artist_name = "Artist One"

    strategy = SeedArtistFallbackStrategy()

    # execute only runs if queries is empty
    await strategy.execute(ctx)
    assert 'artist:"Artist One"' in ctx.queries

    # If queries exist, it does nothing
    ctx2 = StrategyContext(seeds={}, token="tok")
    ctx2.queries.append("existing")
    await strategy.execute(ctx2)
    assert len(ctx2.queries) == 1
    assert "artist:" not in ctx2.queries[0]


@pytest.mark.asyncio
async def test_default_fallback():
    ctx = StrategyContext(seeds={}, token="tok")
    strategy = DefaultFallbackStrategy()
    await strategy.execute(ctx)
    assert "genre:pop" in ctx.queries

    # Does nothing if queries exist
    ctx.queries = ["something"]
    await strategy.execute(ctx)
    assert len(ctx.queries) == 1


@patch("app.services.spotify_client.SpotifyService.get_request", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_resolve_seed_artist_failure(mock_get):
    ctx = StrategyContext(seeds={"seed_tracks": ["bad_track"]}, token="tok")

    # Mock failure
    mock_get.side_effect = Exception("API Error")

    await ctx.resolve_seed_artist()
    assert ctx.seed_artist_id is None
