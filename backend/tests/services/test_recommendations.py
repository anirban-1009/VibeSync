import urllib.parse
from unittest.mock import AsyncMock, patch

import pytest
from app.services.recommendations import get_recommendations


@pytest.mark.asyncio
async def test_get_recommendations_basic():
    token = "test_token"
    seeds = {"seed_tracks": ["t1"]}
    history = []
    targets = {"target_energy": 0.5}

    mock_search_response = {
        "tracks": {
            "items": [
                {"id": "rec1", "name": "Track 1", "artists": [{"name": "A1"}]},
                {"id": "rec2", "name": "Track 2", "artists": [{"name": "A2"}]},
            ]
        }
    }
    mock_track_data = {
        "artists": [{"id": "a1", "name": "Seed Artist", "genres": ["pop"]}]
    }
    mock_artist_data = {"name": "Seed Artist", "genres": ["pop"]}

    with patch(
        "app.services.spotify_client.SpotifyService.get_request",
        new_callable=AsyncMock,
    ) as mock_get:

        def side_effect(url, token, allow_404=False):
            if "/tracks/" in url:
                return mock_track_data
            if "/artists/" in url and "/related-artists" not in url:
                return mock_artist_data
            if "/search" in url:
                return mock_search_response
            return None

        mock_get.side_effect = side_effect

        recs = await get_recommendations(token, seeds, history, targets)
        assert len(recs) >= 1
        ids = [r["id"] for r in recs]
        assert "rec1" in ids or "rec2" in ids


@pytest.mark.asyncio
async def test_get_recommendations_fallback():
    token = "test_token"
    seeds = {}
    history = []
    targets = {}

    mock_search_response = {"tracks": {"items": [{"id": "pop1", "name": "Pop Track"}]}}

    with patch(
        "app.services.spotify_client.SpotifyService.get_request",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = mock_search_response
        recs = await get_recommendations(token, seeds, history, targets)
        assert len(recs) > 0
        assert recs[0]["id"] == "pop1"


@pytest.mark.asyncio
async def test_get_recommendations_complex():
    token = "test_token"
    seeds = {
        "seed_genres": ["rock", "pop", "jazz", "blues"],
        "seed_artists": ["a1"],
    }
    targets = {}

    artist_resp = {"name": "SeedArtist", "genres": ["pop"], "id": "a1"}
    related_resp = {"artists": [{"id": "rel1", "name": "Rel"}]}
    search_resp = {"tracks": {"items": [{"id": "t1", "name": "T1"}]}}

    async def side_effect(url, token, allow_404=False):
        if "related-artists" in url:
            return related_resp
        if "/artists/" in url:
            return artist_resp
        if "/search" in url:
            return search_resp
        return None

    with patch(
        "app.services.spotify_client.SpotifyService.get_request",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.side_effect = side_effect

        recs = await get_recommendations(token, seeds, [], targets)
        assert len(recs) > 0

        search_calls = [
            c[0][0] for c in mock_get.call_args_list if "/search" in c[0][0]
        ]
        unique_qs = set()
        for url in search_calls:
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            if "q" in params:
                unique_qs.add(params["q"][0])
        assert len(unique_qs) <= 3


@pytest.mark.asyncio
async def test_search_retry_success():
    token = "test_token"
    seeds = {"seed_genres": ["rock"]}
    history = []
    targets = {}

    # We want to force offset > 0 to test fallback
    with patch("random.randint") as mock_randint:
        mock_randint.return_value = 10  # Force offset=10

        with patch(
            "app.services.spotify_client.SpotifyService.get_request",
            new_callable=AsyncMock,
        ) as mock_get:

            async def side_effect(url, token, allow_404=False):
                if "offset=10" in url:
                    return None  # Fail first
                if "offset=0" in url:
                    # Success retry
                    return {
                        "tracks": {"items": [{"id": "retry_track", "name": "Retry"}]}
                    }
                return None

            mock_get.side_effect = side_effect

            recs = await get_recommendations(token, seeds, history, targets)

            assert len(recs) > 0
            assert recs[0]["id"] == "retry_track"
