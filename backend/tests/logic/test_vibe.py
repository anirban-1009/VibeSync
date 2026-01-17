from app.logic.vibe import get_vibe_seeds
from app.utils.models import UserVibeData, VibeTrack


def test_get_vibe_seeds():
    # Setup users with partial data
    user1_data = UserVibeData(
        top_tracks=[
            VibeTrack(id="t1", name="S1", artist="A1", uri="u1"),
            VibeTrack(id="t2", name="S2", artist="A1", uri="u2"),
        ]
    )
    user2_data = UserVibeData(
        top_tracks=[
            VibeTrack(id="t1", name="S1", artist="A1", uri="u1"),  # Duplicate ID
            VibeTrack(id="t3", name="S3", artist="A2", uri="u3"),
        ]
    )

    users_data = {"u1": user1_data, "u2": user2_data}

    seeds = get_vibe_seeds(users_data)
    seed_tracks = seeds["seed_tracks"]

    # Should have unique IDs: t1, t2, t3
    assert len(seed_tracks) <= 5
    assert len(seed_tracks) == 3
    assert "t1" in seed_tracks
    assert "t2" in seed_tracks
    assert "t3" in seed_tracks


def test_get_vibe_seeds_limit():
    """Ensure max 5 seeds."""
    tracks = [
        VibeTrack(id=f"t{i}", name=f"S{i}", artist="A", uri=f"u{i}") for i in range(10)
    ]
    user_data = UserVibeData(top_tracks=tracks)

    seeds = get_vibe_seeds({"u1": user_data})
    assert len(seeds["seed_tracks"]) == 5
