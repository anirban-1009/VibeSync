from app.logic.vibe import calculate_room_vibe, get_vibe_seeds
from app.utils.models import UserVibeData


def test_calculate_room_vibe():
    # Mock data
    # User 1: High energy
    user1_data = UserVibeData(
        top_tracks=[
            {
                "id": "1",
                "audio_features": {
                    "energy": 0.8,
                    "valence": 0.8,
                    "danceability": 0.8,
                    "tempo": 120,
                },
            }
        ]
    )
    # User 2: Low energy
    user2_data = UserVibeData(
        top_tracks=[
            {
                "id": "2",
                "audio_features": {
                    "energy": 0.2,
                    "valence": 0.2,
                    "danceability": 0.2,
                    "tempo": 80,
                },
            }
        ]
    )

    users_data = {"u1": user1_data, "u2": user2_data}

    vibe = calculate_room_vibe(users_data)

    assert vibe["target_energy"] == 0.5
    assert vibe["target_tempo"] == 100.0


def test_calculate_room_vibe_empty():
    vibe = calculate_room_vibe({})
    assert vibe["target_energy"] == 0.6
    assert vibe["target_danceability"] == 0.5


def test_calculate_room_vibe_partial_data():
    # User with tracks but missing features
    user1_data = UserVibeData(top_tracks=[{"id": "1", "audio_features": None}])
    vibe = calculate_room_vibe({"u1": user1_data})
    # Should revert to default because no valid features found
    assert vibe["target_energy"] == 0.6


def test_get_vibe_seeds():
    user1_data = UserVibeData(top_tracks=[{"id": "track1"}])
    user2_data = UserVibeData(top_tracks=[{"id": "track2"}])

    users_data = {"u1": user1_data, "u2": user2_data}

    seeds = get_vibe_seeds(users_data)
    assert len(seeds["seed_tracks"]) == 2
    assert "track1" in seeds["seed_tracks"]
    assert "track2" in seeds["seed_tracks"]
