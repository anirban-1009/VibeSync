import uuid

from app.server import sio
from app.services.spotify_client import SpotifyService
from app.state import rooms, sid_map
from app.utils.logger import logger
from app.utils.models import RoomState, RoomUser, Track, UserVibeData


@sio.event
async def connect(sid, environ) -> None:
    logger.debug(f"Socket Connected: {sid}")


@sio.event
async def disconnect(sid) -> None:
    if sid in sid_map:
        user_info = sid_map[sid]
        room_id = user_info.get("room_id")
        user_id = user_info.get("user_id")

        if room_id and room_id in rooms:
            room = rooms[room_id]
            room.users = [u for u in room.users if u.id != user_id]
            await sio.emit("room_state", room.model_dump(), room=room_id)

        del sid_map[sid]


@sio.event
async def join_room(sid, data) -> None:
    room_id = data.get("room_id")
    user_profile = data.get("user_profile")
    # music_service = SpotifyService() # Removed unused instance

    if not room_id:
        return

    await sio.enter_room(sid, room_id)

    # Init room if not exists
    if room_id not in rooms:
        rooms[room_id] = RoomState()

    room = rooms[room_id]

    # Store user info
    if user_profile:
        user = RoomUser(
            id=user_profile.get("id"),
            name=user_profile.get("display_name"),
            image=user_profile.get("images", [{}])[0].get("url")
            if user_profile.get("images")
            else None,
        )
        # Avoid duplicates
        existing = [u for u in room.users if u.id != user.id]
        existing.append(user)
        room.users = existing

        sid_map[sid] = {"room_id": room_id, "user_id": user.id}

        # Fetch Vibe Data (AI DJ)
        token = data.get("token")
        if token:
            try:
                top_tracks = await SpotifyService.fetch_user_top_items(token, "tracks")
                # top_artists = await fetch_user_top_items(token, "artists") # Optimize: fetch only tracks for now to save time/rate limits

                room.vibe_profile.users_data[user.id] = UserVibeData(
                    top_tracks=top_tracks,
                    # top_artists=top_artists
                )
                logger.debug(
                    f"User Vibe Fetched for {user.name}: {len(top_tracks)} tracks."
                )
                if top_tracks:
                    logger.debug(
                        f"Top Track: {top_tracks[0].get('name')} by {top_tracks[0]['artists'][0]['name']}"
                    )
            except Exception as e:
                logger.error(f"Failed to fetch vibe profile for {user.id}: {e}")

    else:
        sid_map[sid] = {"room_id": room_id, "user_id": "anonymous"}

    # Send current state
    await sio.emit("room_state", room.model_dump(), room=sid)
    # Broadcast update
    await sio.emit("room_state", room.model_dump(), room=room_id)


@sio.event
async def leave_session(sid, data) -> None:
    room_id = data.get("room_id")
    if room_id:
        sio.leave_room(sid, room_id)
        if sid in sid_map:
            # Logic similar to disconnect if needed, or just remove from map
            # usually disconnect handles the cleanup
            pass


@sio.event
async def add_to_queue(sid, data) -> None:
    """
    Data: { room_id, track: { uri, name, artist, image, duration_ms } }
    """
    room_id = data.get("room_id")
    track_data = data.get("track")
    logger.debug(
        f"Request to add track: {track_data.get('name') if track_data else 'Unknown'}"
    )

    session = sid_map.get(sid, {})
    user_id = session.get("user_id", "anonymous")

    if room_id and track_data and room_id in rooms:
        room = rooms[room_id]

        new_track = Track(
            uri=track_data.get("uri"),
            name=track_data.get("name"),
            artist=track_data.get("artist"),
            image=track_data.get("image"),
            duration_ms=track_data.get("duration_ms", 0),
            uuid=str(uuid.uuid4()),
            added_by=user_id,
        )

        if room.current_track is None:
            room.current_track = new_track
            room.is_playing = True
            logger.debug(f"Emitting play_track for {new_track.name} in room {room_id}")
            await sio.emit("play_track", new_track.model_dump(), room=room_id)
            await sio.emit("room_state", room.model_dump(), room=room_id)
        else:
            room.queue.append(new_track)
            await sio.emit(
                "queue_updated", [t.model_dump() for t in room.queue], room=room_id
            )
    else:
        logger.warning(
            f"Add to queue failed: Room {room_id} not found or invalid data."
        )


@sio.event
async def toggle_playback(sid, data) -> None:
    room_id = data.get("room_id")
    if room_id in rooms:
        room = rooms[room_id]
        if room.current_track:
            room.is_playing = not room.is_playing
            # Broadcast to all explicitly
            await sio.emit(
                "playback_toggled", {"is_playing": room.is_playing}, room=room_id
            )


@sio.event
async def skip_song(sid, data) -> None:
    room_id = data.get("room_id")
    if room_id in rooms:
        room = rooms[room_id]

        # Add current to history if it exists
        if room.current_track:
            room.history.insert(0, room.current_track)
            # Keep history size manageable
            if len(room.history) > 20:
                room.history.pop()

        if len(room.queue) > 0:
            next_track = room.queue.pop(0)
            room.current_track = next_track
            room.is_playing = True
            await sio.emit("play_track", next_track.model_dump(), room=room_id)
            await sio.emit(
                "room_state", room.model_dump(), room=room_id
            )  # Sync history/queue
        else:
            room.current_track = None
            room.is_playing = False
            await sio.emit("stop_player", room=room_id)
            await sio.emit("room_state", room.model_dump(), room=room_id)


@sio.event
async def remove_from_queue(sid, data) -> None:
    room_id = data.get("room_id")
    track_uuid = data.get("track_uuid")

    if room_id in rooms and track_uuid:
        room = rooms[room_id]
        original_len = len(room.queue)
        room.queue = [t for t in room.queue if t.uuid != track_uuid]

        if len(room.queue) != original_len:
            await sio.emit(
                "queue_updated", [t.model_dump() for t in room.queue], room=room_id
            )
