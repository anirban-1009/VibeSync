from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.events import join_room, set_repeat_mode, set_volume, trigger_dj_voice
from app.utils.models import RoomState, RoomUser, Track


@patch("app.events.sio", new_callable=AsyncMock)
@patch("app.events.sid_map", new_callable=dict)
@patch("app.events.rooms", new_callable=dict)
@patch("app.events.SpotifyService.set_repeat_mode")
@patch("app.events.check_authorization")
@patch("app.events.rate_limiter")
@pytest.mark.asyncio
async def test_set_repeat_mode(
    mock_rate_limiter, mock_auth, mock_set_repeat, mock_rooms, mock_sid_map, mock_sio
):
    room_id = "test_room"
    sid = "test_sid"
    token = "test_token"

    # Grant permissions
    mock_auth.return_value = True
    mock_rate_limiter.check_rate_limit.return_value = True

    mock_rooms[room_id] = RoomState()
    mock_sid_map[sid] = {"room_id": room_id, "user_id": "u1", "token": token}

    # 1. Success case
    mock_set_repeat.return_value = True
    await set_repeat_mode(sid, {"room_id": room_id, "state": "track"})

    mock_set_repeat.assert_called_with(token, "track")
    mock_sio.emit.assert_called_with(
        "repeat_mode_changed", {"state": "track"}, room=room_id
    )

    # 2. No token case (should fail gracefully)
    mock_sid_map[sid] = {"room_id": room_id, "user_id": "u1"}  # No token
    mock_set_repeat.reset_mock()
    mock_sio.reset_mock()

    await set_repeat_mode(sid, {"room_id": room_id, "state": "context"})
    mock_set_repeat.assert_not_called()
    mock_sio.emit.assert_not_called()

    # 3. Token fallback (another user has token)
    other_sid = "other_sid"
    mock_sid_map[other_sid] = {
        "room_id": room_id,
        "user_id": "u2",
        "token": "fallback_token",
    }

    await set_repeat_mode(sid, {"room_id": room_id, "state": "off"})
    mock_set_repeat.assert_called_with("fallback_token", "off")
    mock_sio.emit.assert_called_with(
        "repeat_mode_changed", {"state": "off"}, room=room_id
    )


@patch("app.events.sio", new_callable=AsyncMock)
@patch("app.events.rooms", new_callable=dict)
@patch("app.events.generate_dj_script", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_trigger_dj_voice_logic(mock_gen_script, mock_rooms, mock_sio):
    # Setup
    room_id = "dj_room"
    mock_rooms[room_id] = RoomState(ai_mode_enabled=True)
    room = mock_rooms[room_id]

    # Track with added_by user
    track = Track(
        uri="uri",
        name="Song",
        artist="Artist",
        added_by="u1",
        uuid="123",
        duration_ms=1000,
    )
    user = RoomUser(id="u1", name="Alice")
    room.users = [user]

    mock_gen_script.return_value = "This is DJ AI."

    # Patch where the function is defined: app.services.voice.generate_voice_clip
    with patch(
        "app.services.voice.generate_voice_clip", new_callable=AsyncMock
    ) as mock_voice:
        mock_voice.return_value = "audio_url"

        await trigger_dj_voice(room_id, track)

        mock_gen_script.assert_called()
        mock_sio.emit.assert_called_with(
            "dj_commentary",
            {"text": "This is DJ AI.", "audio_url": "audio_url"},
            room=room_id,
        )

    # Test disabled AI mode
    mock_sio.reset_mock()
    room.ai_mode_enabled = False
    await trigger_dj_voice(room_id, track)
    mock_sio.emit.assert_not_called()


@patch("app.events.SpotifyService.fetch_user_top_items")
@patch("app.events.sio", new_callable=AsyncMock)
@patch("app.events.sid_map", new_callable=dict)
@patch("app.events.rooms", new_callable=dict)
@patch("app.events.cleanup_tasks", new_callable=dict)
@pytest.mark.asyncio
async def test_join_room_fallback_logic(
    mock_cleanup, mock_rooms, mock_sid_map, mock_sio, mock_fetch_top
):
    room_id = "cleanup_cancel_room"
    sid = "sid_join"

    # Setup room in cleanup_tasks
    mock_cleanup[room_id] = MagicMock()

    # Setup Fetch return values with correctly structured items (including URI)
    mock_fetch_top.side_effect = [
        [
            {
                "id": "t1",
                "name": "T1",
                "artists": [{"name": "A1"}],
                "uri": "spotify:track:t1",
            }
        ],
        [
            {
                "id": "t1",
                "name": "T1",
                "artists": [{"name": "A1"}],
                "uri": "spotify:track:t1",
            },
            {
                "id": "t2",
                "name": "T2",
                "artists": [{"name": "A2"}],
                "uri": "spotify:track:t2",
            },
        ],
    ]

    data = {
        "room_id": room_id,
        "user_profile": {"id": "u1", "display_name": "Bob"},
        "token": "valid_token",
    }

    await join_room(sid, data)

    # 1. Cleanup Task Cancelled?
    mock_cleanup[room_id].cancel.assert_called_once()

    # 2. Fetch logic
    assert mock_fetch_top.call_count == 2

    # 3. Correct tracks stored
    room = mock_rooms[room_id]
    user_vibe = room.vibe_profile.users_data["u1"]
    assert len(user_vibe.top_tracks) == 2
    # Check if t1 and t2 are in there
    uris = [t.uri for t in user_vibe.top_tracks]
    assert "spotify:track:t1" in uris
    assert "spotify:track:t2" in uris


@patch("app.events.sio", new_callable=AsyncMock)
@patch("app.events.SpotifyService.set_volume")
@patch("app.events.sid_map", new_callable=dict)
@patch("app.events.rooms", new_callable=dict)
@patch("app.events.check_authorization")
@patch("app.events.rate_limiter")
@pytest.mark.asyncio
async def test_set_volume_event(
    mock_rate_limiter, mock_auth, mock_rooms, mock_sid_map, mock_set_volume, mock_sio
):
    room_id = "vol_room"
    sid = "vol_sid"
    token = "vol_token"

    # Grant permissions
    mock_auth.return_value = True
    mock_rate_limiter.check_rate_limit.return_value = True

    mock_rooms[room_id] = RoomState()
    # Case 1: Active user has token
    mock_sid_map[sid] = {"room_id": room_id, "user_id": "uV", "token": token}

    await set_volume(sid, {"room_id": room_id, "volume": 75})

    mock_set_volume.assert_called_with(token, 75)

    # Case 2: No token for user, finding fallback
    mock_sid_map[sid] = {"room_id": room_id, "user_id": "uV"}  # No token
    other_sid = "other_vol"
    mock_sid_map[other_sid] = {
        "room_id": room_id,
        "user_id": "uFallback",
        "token": "fallback_tok",
    }

    mock_set_volume.reset_mock()
    await set_volume(sid, {"room_id": room_id, "volume": 30})

    mock_set_volume.assert_called_with("fallback_tok", 30)

    # Case 3: No token at all
    mock_sid_map[other_sid] = {
        "room_id": room_id,
        "user_id": "uFallback",
        "token": "",  # Remove token empty
    }

    mock_set_volume.reset_mock()
    await set_volume(sid, {"room_id": room_id, "volume": 50})

    mock_set_volume.assert_not_called()
