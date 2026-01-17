from typing import Any, Dict


def parse_mood(mood_text: str) -> Dict[str, Any]:
    """
    Parse a mood string into Spotify recommendation target parameters.
    Currently uses simple keyword matching.
    TODO: Upgrade to LLM for more complex understanding in Phase 3.
    """
    mood = mood_text.lower()

    if "study" in mood or "focus" in mood or "sleep" in mood:
        return {
            "target_energy": 0.3,
            "target_instrumentalness": 0.8,
            "target_acousticness": 0.7,
            "target_valence": 0.3,
        }

    if "party" in mood or "dance" in mood or "hype" in mood:
        return {"target_energy": 0.85, "target_danceability": 0.8, "min_tempo": 120}

    if "chill" in mood or "relax" in mood:
        return {"target_energy": 0.5, "target_valence": 0.5, "target_acousticness": 0.6}

    if "sad" in mood or "blue" in mood:
        return {"target_valence": 0.2, "target_energy": 0.4}

    if "happy" in mood or "good" in mood:
        return {"target_valence": 0.8, "target_energy": 0.7}

    # Default
    return {}
