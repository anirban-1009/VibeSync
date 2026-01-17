import logging
import uuid
from pathlib import Path

import edge_tts
from app.core.config import Settings
from app.utils.exceptions import TTSGenerationError

logger = logging.getLogger(__name__)

# Directory configuration
# We assume the code runs from 'backend' root, so 'static/voices' is relative to that.
VOICE_DIR = Path("static/voices")
VOICE_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings.get_settings()
BASE_URL = settings.backend_url


async def generate_voice_clip(text: str, voice: str = "en-US-ChristopherNeural") -> str:
    """
    Generate a TTS audio clip using EdgeTTS and save it to the static directory.

    Args:
        text: The text to convert to speech.
        voice: The voice to use (default: en-US-ChristopherNeural).

    Returns:
        str: The full URL to the generated audio file.

    Raises:
        TTSGenerationError: If generation fails.
    """
    try:
        filename = f"{uuid.uuid4()}.mp3"
        file_path = VOICE_DIR / filename

        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(file_path))

        logger.info(f"Generated voice clip: {file_path}")

        # Ensure the path in URL uses forward slashes
        return f"{BASE_URL}/static/voices/{filename}"

    except Exception as e:
        raise TTSGenerationError(f"Failed to generate voice clip: {e}") from e
