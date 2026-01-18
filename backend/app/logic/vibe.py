import random
from typing import Dict, List

from app.utils.models import UserVibeData


def get_vibe_seeds(users_data: Dict[str, UserVibeData]) -> Dict[str, List[str]]:
    """
    Extract seed tracks from the room participants.
    Picks a random track from available users to create a diverse seed list (Max 5).
    """
    seed_tracks = []

    # Collect all available tracks from all users
    all_tracks = []
    for user_data in users_data.values():
        all_tracks.extend(user_data.top_tracks)

    if not all_tracks:
        return {"seed_tracks": []}

    # Shuffle and pick explicit IDs
    random.shuffle(all_tracks)

    # Unique IDs only
    seen = set()
    for t in all_tracks:
        if t.id and t.id not in seen:
            seed_tracks.append(t.id)
            seen.add(t.id)
            if len(seed_tracks) >= 5:
                break

    return {"seed_tracks": seed_tracks}
