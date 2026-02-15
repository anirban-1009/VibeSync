import pytest
from app.utils.exceptions import (
    EnvironmentConfigError,
    LLMGenerationError,
    SpotifyAPIError,
    TTSGenerationError,
    validate_environment_settings,
)


class MockSettings:
    client_id = "cid"
    client_secret = "secret"
    redirect_uri = "uri"
    frontend_url = "url"


def test_exceptions_init():
    # EnvironmentConfigError
    with pytest.raises(EnvironmentConfigError) as exc:
        raise EnvironmentConfigError("Missed config")
    assert "Environment Error: Missed config" in str(exc.value)

    # LLMGenerationError
    with pytest.raises(LLMGenerationError) as exc:
        raise LLMGenerationError("Model failed", provider="OpenAI")
    assert "[OpenAI] Model failed" in str(exc.value)

    # TTSGenerationError
    with pytest.raises(TTSGenerationError) as exc:
        raise TTSGenerationError("TTS failed")
    assert "TTS failed" in str(exc.value)

    # SpotifyAPIError
    with pytest.raises(SpotifyAPIError) as exc:
        raise SpotifyAPIError("Not Found", status_code=404)
    assert "[404] Not Found" in str(exc.value)


def test_validate_environment_settings_success():
    settings = MockSettings()
    values = validate_environment_settings(settings)
    assert values == ("cid", "secret", "uri", "url")


def test_validate_environment_settings_missing():
    settings = MockSettings()
    settings.client_secret = ""  # Missing

    with pytest.raises(EnvironmentConfigError) as exc:
        validate_environment_settings(settings)
    assert "Missing required Spotify configuration: client_secret" in str(exc.value)


def test_validate_environment_settings_invalid_object():
    class BadSettings:
        pass

    with pytest.raises(EnvironmentConfigError) as exc:
        validate_environment_settings(BadSettings())
    assert "Invalid Spotify configuration" in str(exc.value)
