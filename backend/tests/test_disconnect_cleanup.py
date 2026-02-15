import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from app.events import disconnect
from app.utils.models import RoomState, RoomUser

# Capture real sleep for use in side effects
REAL_SLEEP = asyncio.sleep


@patch("app.events.sio", new_callable=AsyncMock)
@patch("app.events.sid_map", new_callable=dict)
@patch("app.events.rooms", new_callable=dict)
@patch("app.events.cleanup_tasks", new_callable=dict)
@patch("app.events.asyncio.sleep", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_disconnect_last_user_pauses_and_cleans_up(
    mock_sleep, mock_cleanup_tasks, mock_rooms, mock_sid_map, mock_sio
):
    # Setup
    room_id = "test_cleanup_room"
    sid = "sid1"
    user_id = "u1"

    # Define side effect:
    # if duration matches 300 (cleanup), return immediately (fast-forward).
    # otherwise (e.g. explicit await asyncio.sleep(0) calls), call REAL_SLEEP.
    async def fast_forward_sleep(seconds):
        if seconds == 300:
            return
        await REAL_SLEEP(seconds)

    mock_sleep.side_effect = fast_forward_sleep

    mock_rooms[room_id] = RoomState()
    room = mock_rooms[room_id]

    # Add user to room
    user = RoomUser(id=user_id, name="Test User")
    room.users = [user]
    room.is_playing = True

    mock_sid_map[sid] = {"room_id": room_id, "user_id": user_id}

    # Act: Disconnect the last user
    await disconnect(sid)

    # Assertions for Disconnect
    assert sid not in mock_sid_map
    assert len(room.users) == 0
    assert room.is_playing is False

    # Check if playback_toggled was emitted with is_playing=False
    playback_emits = [
        call
        for call in mock_sio.emit.call_args_list
        if call[0][0] == "playback_toggled"
    ]
    assert len(playback_emits) == 1
    assert playback_emits[0][0][1] == {"is_playing": False}

    # Yield control to allow background task (cleanup_room) to start/run
    # This calls mock_sleep(0) -> fast_forward_sleep(0) -> await REAL_SLEEP(0)
    await asyncio.sleep(0)
    await asyncio.sleep(0)

    # Assert Cleanup happened
    # mock_sleep should have been called with 300 (inside cleanup_room)
    mock_sleep.assert_any_call(300)

    # Since sleep returned immediately (mock side effect), the cleanup logic should complete.
    # It checks if room is empty. It is.
    # It should delete the room.
    assert room_id not in mock_rooms
