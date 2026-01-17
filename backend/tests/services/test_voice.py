from unittest.mock import AsyncMock, patch

import pytest
from app.services.voice import generate_voice_clip
from app.utils.exceptions import TTSGenerationError


@pytest.fixture
def mock_settings():
    with patch("app.services.voice.settings") as mock:
        mock.backend_url = "http://localhost:8000"
        yield mock


@pytest.mark.asyncio
async def test_generate_voice_clip_success(mock_settings, tmp_path):
    """Test successful voice clip generation."""
    # Mock EdgeTTS Communicate
    with patch("app.services.voice.edge_tts.Communicate") as mock_communicate_cls:
        mock_communicate = mock_communicate_cls.return_value
        # Mock save method to be async
        mock_communicate.save = AsyncMock()

        # We need to mock the VOICE_DIR to point to a temp dir so we don't spam the real fs
        with patch("app.services.voice.VOICE_DIR", tmp_path):
            result = await generate_voice_clip("Hello world", "en-US-test")

            # Check URL format
            assert result.startswith("http://localhost:8000/static/voices/")
            assert result.endswith(".mp3")

            # Verify edge_tts was called
            mock_communicate_cls.assert_called_with("Hello world", "en-US-test")
            mock_communicate.save.assert_called_once()

            # Check file path passed to save
            save_call_args = mock_communicate.save.call_args[0]
            assert str(tmp_path) in save_call_args[0]


@pytest.mark.asyncio
async def test_generate_voice_clip_failure(mock_settings):
    """Test voice clip generation failure."""
    with patch("app.services.voice.edge_tts.Communicate") as mock_communicate_cls:
        mock_communicate = mock_communicate_cls.return_value
        mock_communicate.save = AsyncMock(side_effect=Exception("TTS Error"))

        with pytest.raises(TTSGenerationError):
            await generate_voice_clip("Fail", "en-US-test")
