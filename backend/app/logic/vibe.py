from typing import Dict, List

from app.utils.models import UserVibeData


def calculate_room_vibe(users_data: Dict[str, UserVibeData]) -> Dict[str, float]:
    """
    Calculate the average vibe of the room based on all users' top tracks.
    Returns specific target parameters for Spotify Recommendations (e.g., target_energy).
    """
    total_energy = 0.0
    total_valence = 0.0
    total_danceability = 0.0
    total_tempo = 0.0

    count = 0

    for user_id, data in users_data.items():
        for track in data.top_tracks:
            features = track.get("audio_features")
            if features:
                total_energy += features.get("energy", 0)
                total_valence += features.get("valence", 0)
                total_danceability += features.get("danceability", 0)
                total_tempo += features.get("tempo", 0)
                count += 1

    if count == 0:
        # Default fallback
        return {
            "target_energy": 0.6,
            "target_danceability": 0.5,
            "target_valence": 0.5,
        }

    return {
        "target_energy": round(total_energy / count, 2),
        "target_valence": round(total_valence / count, 2),
        "target_danceability": round(total_danceability / count, 2),
        "target_tempo": round(total_tempo / count, 0),
    }


def get_vibe_seeds(users_data: Dict[str, UserVibeData]) -> Dict[str, List[str]]:
    """
    Extract seed tracks/artists from the room participants.
    We can pick a random selection or most popular.
    """
    # Simple strategy: One track per user, up to 5 users.
    seed_tracks = []

    users = list(users_data.values())
    # TODO: Shuffle or rotate? For now linear.
    for user in users[:5]:
        if user.top_tracks:
            # Pick first one for now
            tid = user.top_tracks[0].get("id")
            if tid:
                seed_tracks.append(tid)

    return {"seed_tracks": seed_tracks}
