from unittest.mock import AsyncMock, patch

import pytest
from app.services.recommendations import get_recommendations


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
