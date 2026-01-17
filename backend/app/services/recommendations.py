import statistics
from typing import Any, Dict, List

from app.services.spotify_client import SpotifyService
from app.utils.logger import logger
from app.utils.models import Track


async def get_recommendations(
    token: str,
    seeds: Dict[str, List[str]],
    history: List[Track],
    targets: Dict[str, Any],
) -> List[dict]:
    """
    Get recommendations based on seeds and adjusted by history vibe.
    Returns a list of raw track dictionaries from Spotify API.
    """

    # 1. Analyze History for "Vibe Validation"
    # We only care about the last 5 tracks
    recent_history = history[-5:] if len(history) >= 5 else history

    if recent_history:
        try:
            # Extract IDs
            track_ids = []
            for track in recent_history:
                # uri format: "spotify:track:ID"
                if track.uri and "spotify:track:" in track.uri:
                    track_ids.append(track.uri.split(":")[-1])

            if track_ids:
                features = await SpotifyService.get_audio_features(token, track_ids)
                # Filter out None values just in case
                features = [f for f in features if f]

                if len(features) >= 2:
                    energies = [f.get("energy", 0) for f in features]
                    tempos = [f.get("tempo", 0) for f in features]

                    energy_std = statistics.stdev(energies) if len(energies) > 1 else 0
                    tempo_std = statistics.stdev(tempos) if len(tempos) > 1 else 0

                    logger.info(
                        f"Vibe Analysis: Energy STD={energy_std:.2f}, Tempo STD={tempo_std:.2f}"
                    )

                    # If variance is low, it means the playlist is monotonous.
                    # We might want to inject some variety.
                    if energy_std < 0.05:
                        # Very consistent energy. Let's shift the target slightly.
                        current_avg_energy = statistics.mean(energies)

                        # Logic: If energy is monotonously high (>0.7), try to bring it down slightly.
                        # If low (<0.4), try to bring it up.
                        # If middle, just gently vary it.

                        target_energy = targets.get("target_energy", current_avg_energy)

                        if current_avg_energy > 0.7:
                            targets["target_energy"] = max(0.4, target_energy - 0.2)
                        elif current_avg_energy < 0.4:
                            targets["target_energy"] = min(0.7, target_energy + 0.2)
                        else:
                            targets["target_energy"] = min(0.9, target_energy + 0.1)

                        logger.info(
                            f"Monotonous vibe detected (Mean Energy: {current_avg_energy:.2f}). "
                            f"Shifting target to {targets['target_energy']:.2f}"
                        )

        except Exception as e:
            logger.error(f"Error analyzing history vibe: {e}")

    # 2. Build Query
    # seeds = {'seed_tracks': [...], 'seed_artists': [...], 'seed_genres': [...]}
    query_params = {**targets, "limit": 10}

    # Add seeds to query params
    for key in ["seed_tracks", "seed_artists", "seed_genres"]:
        if key in seeds and seeds[key]:
            query_params[key] = ",".join(
                seeds[key][:5]
            )  # Spotify allows max 5 seeds total

    # 3. Call API
    query_str = "&".join([f"{k}={v}" for k, v in query_params.items()])
    url = f"{SpotifyService.BASE_URL}/recommendations?{query_str}"

    data = await SpotifyService.get_request(url, token)

    if data and "tracks" in data:
        return data["tracks"]

    return []
