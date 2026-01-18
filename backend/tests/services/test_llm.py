from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.llm import (
    GeminiClient,
    OllamaClient,
    OpenAIClient,
    generate_dj_script,
    get_llm_client,
)
from app.utils.exceptions import LLMGenerationError


@pytest.fixture
def mock_settings():
    with patch("app.services.llm.Settings.get_settings") as mock:
        yield mock.return_value


@pytest.fixture
def safe_context():
    return {
        "current_song_name": "Song",
        "current_song_artist": "Artist",
        "next_song_name": "Next Song",
        "next_song_artist": "Next Artist",
        "added_by_user": "User",
        "vibe_description": "Chill",
    }


@pytest.mark.asyncio
async def test_get_llm_client_gemini(mock_settings):
    """Test factory returns GeminiClient when configured."""
    mock_settings.gemini_api_key = "test_gemini"
    mock_settings.gemini_model = "gemini-pro"
    mock_settings.openai_api_key = None

    client = get_llm_client()
    assert isinstance(client, GeminiClient)
    assert client.api_key == "test_gemini"
    assert client.model == "gemini-pro"


@pytest.mark.asyncio
async def test_get_llm_client_openai(mock_settings):
    """Test factory returns OpenAIClient when configured and Gemini is missing."""
    mock_settings.gemini_api_key = None
    mock_settings.openai_api_key = "test_openai"
    mock_settings.openai_model = "gpt-4"

    client = get_llm_client()
    assert isinstance(client, OpenAIClient)
    assert client.api_key == "test_openai"
    assert client.model == "gpt-4"


@pytest.mark.asyncio
async def test_get_llm_client_ollama(mock_settings):
    """Test factory defaults to OllamaClient when others are missing."""
    mock_settings.gemini_api_key = None
    mock_settings.openai_api_key = None
    mock_settings.ollama_url = "http://test-ollama"
    mock_settings.ollama_model = "llama2-test"

    client = get_llm_client()
    assert isinstance(client, OllamaClient)
    assert client.base_url == "http://test-ollama"
    assert client.model == "llama2-test"


@pytest.mark.asyncio
async def test_openai_generate():
    """Test OpenAI client generation success."""
    client = OpenAIClient(api_key="test_key", model="test-model")

    response_mock = MagicMock()
    response_mock.json.return_value = {
        "choices": [{"message": {"content": "Hello World"}}]
    }
    response_mock.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = response_mock

        result = await client.generate("Sys", "User")

        assert result == "Hello World"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["model"] == "test-model"
        assert kwargs["headers"]["Authorization"] == "Bearer test_key"


@pytest.mark.asyncio
async def test_openai_generate_failure():
    """Test OpenAI client generation failure."""
    client = OpenAIClient(api_key="test_key")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = Exception("API fail")

        with pytest.raises(LLMGenerationError):
            await client.generate("Sys", "User")


@pytest.mark.asyncio
async def test_gemini_generate():
    """Test Gemini client generation success."""
    client = GeminiClient(api_key="test_key", model="gemini-pro")

    response_mock = MagicMock()
    response_mock.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Gemini Response"}]}}]
    }
    response_mock.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = response_mock

        result = await client.generate("Sys", "User")

        assert result == "Gemini Response"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["params"]["key"] == "test_key"
        # Check that URL contains the model
        assert "v1beta/models/gemini-pro:generateContent" in client.url


@pytest.mark.asyncio
async def test_gemini_generate_failure():
    """Test Gemini client generation failure."""
    client = GeminiClient(api_key="test_key")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = Exception("API fail")

        with pytest.raises(LLMGenerationError):
            await client.generate("Sys", "User")


@pytest.mark.asyncio
async def test_ollama_generate():
    """Test Ollama client generation success."""
    client = OllamaClient(base_url="http://localhost", model="llama2")

    response_mock = MagicMock()
    response_mock.json.return_value = {"response": "Ollama Output"}
    response_mock.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = response_mock

        result = await client.generate("Sys", "User")

        assert result == "Ollama Output"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["model"] == "llama2"


@pytest.mark.asyncio
async def test_ollama_generate_failure():
    """Test Ollama client generation failure."""
    client = OllamaClient(base_url="http://localhost")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = Exception("API fail")

        with pytest.raises(LLMGenerationError):
            await client.generate("Sys", "User")


@pytest.mark.asyncio
async def test_generate_dj_script_success(safe_context):
    """Test generate_dj_script uses the client successfully."""
    mock_client = AsyncMock()
    mock_client.generate.return_value = "Generated Script"

    with patch("app.services.llm.get_llm_client", return_value=mock_client):
        context = safe_context

        result = await generate_dj_script(context)

        assert result == "Generated Script"
        mock_client.generate.assert_called_once()


@pytest.mark.asyncio
async def test_generate_dj_script_failure(safe_context):
    """Test generate_dj_script fallback on error."""
    mock_client = AsyncMock()
    mock_client.generate.side_effect = LLMGenerationError("API Error")

    with patch("app.services.llm.get_llm_client", return_value=mock_client):
        # We must provide context to avoid KeyError during string formatting
        # BEFORE it even hits the API call loop if not handled
        result = await generate_dj_script(safe_context)

        # Check valid fallback
        assert "Hey everyone" in result
        assert "great track" in result
