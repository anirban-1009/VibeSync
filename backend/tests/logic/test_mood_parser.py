from unittest.mock import MagicMock, patch

import pytest
from app.logic.mood_parser import parse_mood


@pytest.mark.asyncio
async def test_parse_mood_llm_success():
    """Test that LLM result is used when successful."""
    with patch("app.logic.mood_parser.get_llm_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        async def mock_generate(*args, **kwargs):
            return '{"seed_genres": ["techno", "electronic"], "target_energy": 0.9}'

        mock_client.generate = mock_generate

        result = await parse_mood("Generate high energy music")
        assert result["seed_genres"] == ["techno", "electronic"]
        assert result["target_energy"] == 0.9


@pytest.mark.asyncio
async def test_parse_mood_fallback_study():
    """Test fallback logic when LLM fails."""
    with patch("app.logic.mood_parser.get_llm_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        async def mock_fail(*args, **kwargs):
            raise Exception("Simulated LLM Failure")

        mock_client.generate = mock_fail

        result = await parse_mood("I want study mode")
        assert result["seed_genres"] == ["classical", "ambient", "study"]


@pytest.mark.asyncio
async def test_parse_mood_fallback_party():
    with patch("app.logic.mood_parser.get_llm_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.generate = MagicMock(side_effect=Exception("Fail"))

        # AsyncMock for generate wouldn't work easily with side_effect exception
        # unless configured well, so we use explicit async func above.
        # Let's stick to the pattern that works.
        async def mock_fail(*args, **kwargs):
            raise Exception("Fail")

        mock_client.generate = mock_fail

        result = await parse_mood("Let's party hard")
        assert result["seed_genres"] == ["pop", "dance", "house"]
        assert result["target_popularity"] == 80


@pytest.mark.asyncio
async def test_parse_mood_fallback_chill():
    with patch("app.logic.mood_parser.get_llm_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        async def mock_fail(*args, **kwargs):
            raise Exception("Fail")

        mock_client.generate = mock_fail

        result = await parse_mood("chill vibes")
        assert result["seed_genres"] == ["acoustic", "chill", "indie-pop"]


@pytest.mark.asyncio
async def test_parse_mood_unknown_fallback():
    with patch("app.logic.mood_parser.get_llm_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        async def mock_fail(*args, **kwargs):
            raise Exception("Fail")

        mock_client.generate = mock_fail

        result = await parse_mood("random string")
        assert result == {}
