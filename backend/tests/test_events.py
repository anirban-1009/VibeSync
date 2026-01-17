from unittest.mock import AsyncMock, patch

import pytest
from app.events import (
    add_to_queue,
    disconnect,
    join_room,
    remove_from_queue,
    skip_song,
    toggle_playback,
)
from app.utils.models import RoomState, Track


@patch("app.events.sio", new_callable=AsyncMock)
@patch("app.events.sid_map", new_callable=dict)
@patch("app.events.rooms", new_callable=dict)
@pytest.mark.asyncio
async def test_add_to_queue(mock_rooms, mock_sid_map, mock_sio):
    # Setup state
    room_id = "test_room"
    sid = "test_sid"
    user_id = "user1"

    mock_rooms[room_id] = RoomState()
    mock_sid_map[sid] = {"room_id": room_id, "user_id": user_id}

    data = {
        "room_id": room_id,
        "track": {
            "uri": "spotify:track:1",
            "name": "Song 1",
            "artist": "Artist 1",
            "duration_ms": 1000,
            "image": "img_url",
        },
    }

    await add_to_queue(sid, data)

    # Assertions
    room = mock_rooms[room_id]
    assert room.is_playing
    assert room.current_track.name == "Song 1"
    assert room.current_track.added_by == user_id

    # Check emits
    assert mock_sio.emit.call_count >= 2  # play_track, room_state


@patch("app.events.SpotifyService.fetch_user_top_items")
@patch("app.events.sio", new_callable=AsyncMock)
@patch("app.events.sid_map", new_callable=dict)
@patch("app.events.rooms", new_callable=dict)
@pytest.mark.asyncio
async def test_join_room_new(mock_rooms, mock_sid_map, mock_sio, mock_fetch_top):
    # Setup
    sid = "test_sid"
    room_id = "new_room"

    user_profile = {
        "id": "u1",
        "display_name": "User 1",
        "images": [{"url": "http://img.com"}],
    }

    data = {"room_id": room_id, "user_profile": user_profile, "token": "tok"}

    # Mock responses
    mock_fetch_top.return_value = [
        {
            "id": "t1",
            "name": "Track 1",
            "artists": [{"name": "A1"}],
            "uri": "spotify:track:t1",
        }
    ]

    await join_room(sid, data)

    assert room_id in mock_rooms
    room = mock_rooms[room_id]
    assert len(room.users) == 1
    assert room.users[0].id == "u1"

    # Verify vibe integration
    user_vibe = room.vibe_profile.users_data["u1"]
    assert len(user_vibe.top_tracks) == 1

    # Check VibeTrack conversion
    track = user_vibe.top_tracks[0]
    assert track.id == "t1"
    assert track.name == "Track 1"
    assert track.artist == "A1"

    mock_sio.enter_room.assert_called_with(sid, room_id)


@patch("app.events.sio", new_callable=AsyncMock)
@patch("app.events.sid_map", new_callable=dict)
@patch("app.events.rooms", new_callable=dict)
@pytest.mark.asyncio
async def test_skip_song(mock_rooms, mock_sid_map, mock_sio):
    room_id = "r1"
    mock_rooms[room_id] = RoomState()
    room = mock_rooms[room_id]

    # 1. Skip with empty queue (stop player)
    await skip_song("sid", {"room_id": room_id})
    assert room.is_playing is False
    assert room.current_track is None
    # Expect stop_player emit
    args, _ = mock_sio.emit.call_args_list[-2]  # Second to last should be stop_player
    assert args[0] == "stop_player"

    # 2. Skip with queue
    t1 = Track(uri="1", name="1", artist="a", duration_ms=100)
    t2 = Track(uri="2", name="2", artist="b", duration_ms=100)

    room.current_track = t1
    room.queue = [t2]
    room.is_playing = True

    await skip_song("sid", {"room_id": room_id})

    assert room.current_track == t2
    assert len(room.queue) == 0
    assert len(room.history) == 1
    assert room.history[0] == t1


@patch("app.events.sio", new_callable=AsyncMock)
@patch("app.events.sid_map", new_callable=dict)
@patch("app.events.rooms", new_callable=dict)
@pytest.mark.asyncio
async def test_disconnect_leave(mock_rooms, mock_sid_map, mock_sio):
    room_id = "r1"
    sid = "sid1"
    user_id = "u1"

    mock_rooms[room_id] = RoomState()
    mock_sid_map[sid] = {"room_id": room_id, "user_id": user_id}

    # Add dummy user to room
    # Note: RoomUser setup required if we strictly typed checks, but logic uses id comparison
    # mock_rooms[room_id].users ... (skipped for brevity unless needed)

    await disconnect(sid)

    assert sid not in mock_sid_map
    # Check if emit happened (room_state update)
    assert mock_sio.emit.called


@patch("app.events.sio", new_callable=AsyncMock)
@patch("app.events.sid_map", new_callable=dict)
@patch("app.events.rooms", new_callable=dict)
@pytest.mark.asyncio
async def test_toggle_playback(mock_rooms, mock_sid_map, mock_sio):
    room_id = "r1"
    mock_rooms[room_id] = RoomState()
    room = mock_rooms[room_id]
    room.current_track = Track(uri="1", name="1", artist="a", duration_ms=100)
    room.is_playing = False

    await toggle_playback("sid", {"room_id": room_id})

    assert room.is_playing is True
    # assert emit playback_toggled


@patch("app.events.sio", new_callable=AsyncMock)
@patch("app.events.sid_map", new_callable=dict)
@patch("app.events.rooms", new_callable=dict)
@pytest.mark.asyncio
async def test_remove_from_queue(mock_rooms, mock_sid_map, mock_sio):
    room_id = "r1"
    mock_rooms[room_id] = RoomState()
    room = mock_rooms[room_id]

    t1 = Track(uri="1", name="1", artist="a", duration_ms=100, uuid="uuid1")
    room.queue = [t1]

    await remove_from_queue("sid", {"room_id": room_id, "track_uuid": "uuid1"})

    assert len(room.queue) == 0
