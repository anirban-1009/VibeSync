from typing import TYPE_CHECKING

from app.utils.logger import logger

if TYPE_CHECKING:
    from app.core.config import Settings


class EnvironmentConfigError(Exception):
    """Raised when environment configuration is invalid or missing."""

    def __init__(self, message: str):
        logger.error("Environment Error: " + message)
        super().__init__("Environment Error: " + message)


class LLMGenerationError(Exception):
    """Raised when LLM text generation fails."""

    def __init__(self, message: str, provider: str = "Unknown"):
        self.message = f"[{provider}] {message}"
        logger.error(f"LLM Error: {self.message}")
        super().__init__(self.message)


class TTSGenerationError(Exception):
    """Raised when Text-to-Speech generation fails."""

    def __init__(self, message: str):
        logger.error(f"TTS Error: {message}")
        super().__init__(message)


class SpotifyAPIError(Exception):
    """Raised when critical Spotify API calls fail."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = f"[{status_code}] {message}"
        logger.error(f"Spotify API Error: {self.message}")
        super().__init__(self.message)


def validate_environment_settings(settings: "Settings") -> tuple[str, str, str, str]:
    """
    Extracts and validates environment settings.

    Raises:
        EnvironmentConfigError: If any required setting is missing or empty.
    """
    required_fields = ("client_id", "client_secret", "redirect_uri", "frontend_url")
    try:
        values = tuple(getattr(settings, field) for field in required_fields)
        if not all(values):
            missing = [f for f, v in zip(required_fields, values) if not v]
            raise EnvironmentConfigError(
                f"Missing required Spotify configuration: {', '.join(missing)}"
            )
        return values
    except AttributeError as e:
        raise EnvironmentConfigError(f"Invalid Spotify configuration: {e}") from e
