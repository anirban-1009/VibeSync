from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.spotify_client import SpotifyService


@pytest.mark.asyncio
async def test_get_request_success():
    token = "valid_token"
    url = "https://api.spotify.com/v1/test"
    mock_json = {"key": "value"}

    # Mock httpx response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_json

    # Mock httpx.AsyncClient
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        result = await SpotifyService.get_request(url, token)

        assert result == mock_json
        mock_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_request_failure():
    token = "valid_token"
    url = "https://api.spotify.com/v1/fail"

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Error"

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        # Should log error and return None
        result = await SpotifyService.get_request(url, token)

        assert result is None


@pytest.mark.asyncio
async def test_get_request_exception():
    token = "valid_token"
    url = "https://api.spotify.com/v1/error"

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("Connection error")
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        result = await SpotifyService.get_request(url, token)
        assert result is None


@pytest.mark.asyncio
async def test_put_request_success():
    token = "token"
    url = "url"
    payload = {"k": "v"}

    mock_response = MagicMock()
    mock_response.status_code = 204

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        # Mock put
        mock_client.put.return_value = mock_response
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        result = await SpotifyService._put(url, token, payload)
        assert result is True


@pytest.mark.asyncio
async def test_put_request_failure():
    token = "token"
    url = "url"

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Error"

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.put.return_value = mock_response
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        result = await SpotifyService._put(url, token)
        assert result is False


@pytest.mark.asyncio
async def test_put_request_exception():
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.put.side_effect = Exception("Net error")
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        result = await SpotifyService._put("url", "token")
        assert result is False


@pytest.mark.asyncio
async def test_get_audio_features_chunking():
    token = "token"
    ids = ["1", "2"]

    mock_data = {"audio_features": [{"id": "1"}, {"id": "2"}]}

    with patch(
        "app.services.spotify_client.SpotifyService._get", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_data

        features = await SpotifyService.get_audio_features(token, ids)

        assert len(features) == 2

        args, _ = mock_get.call_args
        url = args[0]
        assert "ids=1,2" in url


@pytest.mark.asyncio
async def test_get_audio_features_empty():
    features = await SpotifyService.get_audio_features("token", [])
    assert features == []


@pytest.mark.asyncio
async def test_fetch_user_top_items():
    mock_data = {"items": [{"name": "Song"}]}
    with patch(
        "app.services.spotify_client.SpotifyService._get", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_data
        items = await SpotifyService.fetch_user_top_items("tok")
        assert len(items) == 1
        assert items[0]["name"] == "Song"
