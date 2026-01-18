import json
from typing import Any, Dict

from app.services.llm import get_llm_client
from app.utils.logger import logger

MOOD_PARSER_SYSTEM_PROMPT = """
You are an expert music curator and mood analyst.
Your goal is to translate a natural language mood description into a list of Spotify Genre Seeds.

Output strictly valid JSON with no markdown formatting.
The JSON keys should be:
- seed_genres: List[str] (Max 3 genres)
- target_popularity: int (Optional, 0-100)

Valid Spotify genres examples: "pop", "rock", "hip-hop", "ambient", "classical", "jazz", "edm", "house", "techno", "indie", "sleep", "study", "party".
Select the best matching genres.

Do not explain. Return ONLY the JSON object.
"""


def _parse_mood_fallback(mood_text: str) -> Dict[str, Any]:
    """Fallback simple keyword matching if LLM fails."""
    mood = mood_text.lower()

    if "study" in mood or "focus" in mood or "sleep" in mood:
        return {"seed_genres": ["classical", "ambient", "study"]}

    if "party" in mood or "dance" in mood or "hype" in mood:
        return {"seed_genres": ["pop", "dance", "house"], "target_popularity": 80}

    if "chill" in mood or "relax" in mood:
        return {"seed_genres": ["acoustic", "chill", "indie-pop"]}

    if "sad" in mood or "blue" in mood:
        return {"seed_genres": ["sad", "rainy-day", "piano"]}

    if "happy" in mood or "good" in mood:
        return {"seed_genres": ["pop", "happy", "summer"]}

    # Default
    return {}


async def parse_mood(mood_text: str) -> Dict[str, Any]:
    """
    Parse a mood string into Spotify recommendation target parameters.
    Uses LLM for complex understanding, falls back to keywords on error.
    """
    client = get_llm_client()

    try:
        response = await client.generate(
            system_prompt=MOOD_PARSER_SYSTEM_PROMPT, user_prompt=f"Mood: {mood_text}"
        )
        clean_response = response.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_response)
    except Exception as e:
        logger.error(f"LLM Mood Parsing failed: {e}")
        return _parse_mood_fallback(mood_text)
