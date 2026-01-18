from unittest.mock import AsyncMock, patch

import pytest
from app.events import add_to_queue
from app.utils.models import RoomState, RoomUser


@patch("app.events.generate_dj_script")
@patch("app.events.sio", new_callable=AsyncMock)
@patch("app.events.sid_map", new_callable=dict)
@patch("app.events.rooms", new_callable=dict)
@pytest.mark.asyncio
async def test_dj_commentary_on_play(
    mock_rooms, mock_sid_map, mock_sio, mock_generate_script
):
    # Setup state
    room_id = "test_room_dj"
    sid = "test_sid"
    user_id = "user1"

    # Ensure AI mode is enabled
    mock_rooms[room_id] = RoomState(ai_mode_enabled=True)
    # Add a user to the room so we can resolve names
    user = RoomUser(id=user_id, name="DJ Fan")
    mock_rooms[room_id].users = [user]

    mock_sid_map[sid] = {"room_id": room_id, "user_id": user_id}

    mock_generate_script.return_value = "Hello World DJ"

    data = {
        "room_id": room_id,
        "track": {
            "uri": "spotify:track:1",
            "name": "Song 1",
            "artist": "Artist 1",
            "duration_ms": 1000,
            "image": "img_url",
            # This triggers the name lookup path
        },
    }
    # Track model creation inside add_to_queue uses sid->user_id to set added_by
    # So the Track.added_by will be "user1"

    # Mock the voice generation to ensure we don't call external services
    # We patch it where it is imported in events.py (or expected to be imported)
    # Since events.py does `from app.services.voice import generate_voice_clip` inside the function,
    # patch 'app.services.voice.generate_voice_clip' effectively.
    with patch(
        "app.services.voice.generate_voice_clip", new_callable=AsyncMock
    ) as mock_voice:
        mock_voice.return_value = "http://test-url/voice.mp3"

        # Action: add_to_queue (will trigger play since queue empty)
        await add_to_queue(sid, data)

        # Check if generate_dj_script was called
        assert mock_generate_script.called

        # Check if dj_commentary was emitted
        found = False
        for call in mock_sio.emit.call_args_list:
            args, _ = call
            if args[0] == "dj_commentary":
                # Verify payload structure matches new implementation
                assert args[1] == {
                    "text": "Hello World DJ",
                    "audio_url": "http://test-url/voice.mp3",
                }
                found = True
                break

        assert found
