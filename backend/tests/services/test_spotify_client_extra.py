from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.spotify_client import SpotifyService
from app.utils.exceptions import SpotifyAPIError


@pytest.mark.asyncio
async def test_get_allow_404():
    url = "http://api/404"
    token = "tok"

    mock_resp = MagicMock()
    mock_resp.status_code = 404

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        # 1. allow_404=True -> returns None
        res = await SpotifyService._get(url, token, allow_404=True)
        assert res is None

        # 2. allow_404=False -> logs error (returns None in implementation)
        # Check logs if possible, or just return value
        res2 = await SpotifyService._get(url, token, allow_404=False)
        assert res2 is None


@pytest.mark.asyncio
async def test_fetch_user_top_items_error():
    with patch("app.services.spotify_client.SpotifyService._get") as mock_get:
        mock_get.return_value = None

        with pytest.raises(SpotifyAPIError):
            await SpotifyService.fetch_user_top_items("tok")


@pytest.mark.asyncio
async def test_set_repeat_mode():
    token = "tok"

    # invalid state
    assert await SpotifyService.set_repeat_mode(token, "invalid") is False

    with patch("app.services.spotify_client.SpotifyService._put") as mock_put:
        mock_put.return_value = True

        # Valid state
        assert await SpotifyService.set_repeat_mode(token, "track") is True
        mock_put.assert_called_with(
            "https://api.spotify.com/v1/me/player/repeat?state=track", token
        )
