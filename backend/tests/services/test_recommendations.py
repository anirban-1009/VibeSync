from unittest.mock import AsyncMock, patch

import pytest
from app.services.recommendations import get_recommendations
from app.utils.models import Track


@pytest.mark.asyncio
async def test_get_recommendations_basic():
    token = "test_token"
    seeds = {"seed_tracks": ["t1", "t2"]}
    history = []
    targets = {"target_energy": 0.5}

    mock_response = {"tracks": [{"id": "rec1"}, {"id": "rec2"}]}

    with patch(
        "app.services.recommendations.SpotifyService.get_request",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = mock_response

        recs = await get_recommendations(token, seeds, history, targets)

        assert len(recs) == 2
        assert recs[0]["id"] == "rec1"

        # Verify call args
        args, _ = mock_get.call_args
        url = args[0]
        assert "target_energy=0.5" in url
        assert "seed_tracks=t1,t2" in url


@pytest.mark.asyncio
async def test_get_recommendations_vibe_adjustment():
    token = "test_token"
    seeds = {"seed_tracks": ["t1"]}
    targets = {"target_energy": 0.8}

    # Create history with monotonous high energy
    history = [
        Track(uri="spotify:track:1", name="1", artist="a", duration_ms=100),
        Track(uri="spotify:track:2", name="2", artist="a", duration_ms=100),
    ]

    # Mock audio features returning high energy
    mock_features = [
        {"id": "1", "energy": 0.8, "tempo": 120},
        {"id": "2", "energy": 0.81, "tempo": 122},
    ]

    mock_response = {"tracks": []}

    with patch(
        "app.services.recommendations.SpotifyService.get_audio_features",
        new_callable=AsyncMock,
    ) as mock_features_call:
        with patch(
            "app.services.recommendations.SpotifyService.get_request",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_features_call.return_value = mock_features
            mock_get.return_value = mock_response

            await get_recommendations(token, seeds, history, targets)

            # Check if target_energy was adjusted down (chill logic)
            # Original was 0.8. Avg ~0.805. High energy logic -> max(0.4, target - 0.2)
            # 0.8 - 0.2 = 0.6.
            # We check the URL passed to get_request
            args, _ = mock_get.call_args
            url = args[0]
            # It's hard to check exact float string, but let's check it changed
            assert "target_energy=0.6" in url or "target_energy=0.60" in url


@pytest.mark.asyncio
async def test_get_recommendations_no_history():
    token = "test_token"
    seeds = {}
    history = []
    targets = {}

    with patch(
        "app.services.recommendations.SpotifyService.get_request",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = {"tracks": []}
        await get_recommendations(token, seeds, history, targets)
        assert mock_get.called
