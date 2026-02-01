from unittest.mock import AsyncMock, patch

import pytest
from app.services.recommendations import get_recommendations


@pytest.mark.asyncio
async def test_get_recommendations_basic():
    token = "test_token"
    seeds = {"seed_tracks": ["t1"]}
    history = []
    targets = {"target_energy": 0.5}

    # The new logic expects search results in data['tracks']['items']
    mock_search_response = {
        "tracks": {
            "items": [
                {"id": "rec1", "name": "Track 1", "artists": [{"name": "A1"}]},
                {"id": "rec2", "name": "Track 2", "artists": [{"name": "A2"}]},
            ]
        }
    }

    # Mock track details for seed resolution
    mock_track_data = {
        "artists": [{"id": "a1", "name": "Seed Artist", "genres": ["pop"]}]
    }

    # Mock artist details
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

        # We generally expect results if the search returns items
        assert len(recs) >= 1
        # The result logic shuffles, so we just check presence
        ids = [r["id"] for r in recs]
        assert "rec1" in ids or "rec2" in ids


@pytest.mark.asyncio
async def test_get_recommendations_fallback():
    token = "test_token"
    seeds = {}  # No seeds -> triggers default pop fallback
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
