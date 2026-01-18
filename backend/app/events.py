import uuid

from app.server import sio
from app.services.llm import generate_dj_script
from app.services.spotify_client import SpotifyService
from app.state import rooms, sid_map
from app.utils.logger import logger
from app.utils.models import RoomState, RoomUser, Track, UserVibeData, VibeTrack


async def trigger_dj_voice(room_id: str, current_track: Track) -> None:
    """Helper to generate and emit DJ commentary."""
    room = rooms.get(room_id)
    if not room or not room.ai_mode_enabled:
        return

    try:
        next_song = room.queue[0] if room.queue else None

        added_by_name = "someone"
        if current_track.added_by and current_track.added_by not in (
            "system",
            "anonymous",
        ):
            for u in room.users:
                if u.id == current_track.added_by:
                    added_by_name = u.name
                    break

        context = {
            "current_song_name": current_track.name,
            "current_song_artist": current_track.artist,
            "next_song_name": next_song.name if next_song else "nothing queued",
            "next_song_artist": next_song.artist if next_song else "unknown",
            "added_by_user": added_by_name,
            "vibe_description": "keeping it fresh",
        }

        script = await generate_dj_script(context)

        audio_url = None
        if script:
            try:
                from app.services.voice import generate_voice_clip

                audio_url = await generate_voice_clip(script)
            except Exception as e:
                logger.error(f"TTS generation failed: {e}")

        if script:
            await sio.emit(
                "dj_commentary", {"text": script, "audio_url": audio_url}, room=room_id
            )
            logger.info(f"DJ Commentary emitted for room {room_id}")

    except Exception as e:
        logger.error(f"Failed to generate DJ commentary: {e}")


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
    music_service = SpotifyService()

    if not room_id:
        return

    await sio.enter_room(sid, room_id)

    if room_id not in rooms:
        rooms[room_id] = RoomState()

    room = rooms[room_id]

    if user_profile and user_profile.get("id"):
        user = RoomUser(
            id=user_profile.get("id"),
            name=user_profile.get("display_name"),
            image=user_profile.get("images", [{}])[0].get("url")
            if user_profile.get("images")
            else None,
        )
        existing = [u for u in room.users if u.id != user.id]
        existing.append(user)
        room.users = existing

        sid_map[sid] = {"room_id": room_id, "user_id": user.id}

        token = data.get("token")
        if token:
            try:
                raw_tracks = await music_service.fetch_user_top_items(
                    token, "tracks", limit=20, time_range="short_term"
                )

                if not raw_tracks or len(raw_tracks) < 5:
                    logger.debug(
                        f"User {user.name} has few short-term tracks ({len(raw_tracks)}), fetching medium-term."
                    )
                    try:
                        medium_tracks = await music_service.fetch_user_top_items(
                            token, "tracks", limit=20, time_range="medium_term"
                        )
                        existing_ids = {t["id"] for t in raw_tracks if "id" in t}
                        for t in medium_tracks:
                            if t.get("id") and t["id"] not in existing_ids:
                                raw_tracks.append(t)
                                existing_ids.add(t["id"])
                    except Exception as e:
                        logger.warning(
                            f"Failed to fetch medium-term fallback for {user.name}: {e}"
                        )

                refined_tracks = []

                if raw_tracks:
                    for t in raw_tracks:
                        artist_name = "Unknown"
                        if t.get("artists") and len(t["artists"]) > 0:
                            artist_name = t["artists"][0].get("name", "Unknown")

                        refined_tracks.append(
                            VibeTrack(
                                id=t.get("id"),
                                name=t.get("name"),
                                artist=artist_name,
                                uri=t.get("uri"),
                                popularity=t.get("popularity"),
                                explicit=t.get("explicit"),
                                album=t.get("album", {}).get("name"),
                            )
                        )

                room.vibe_profile.users_data[user.id] = UserVibeData(
                    top_tracks=refined_tracks,
                )

                logger.debug(
                    f"User Vibe Fetched for {user.name}: {len(refined_tracks)} tracks saved."
                )
                if refined_tracks:
                    logger.debug(
                        f"Top Vibe Track: {refined_tracks[0].name} by {refined_tracks[0].artist}"
                    )

            except Exception as e:
                logger.error(f"Failed to fetch vibe profile for {user.id}: {e}")

    else:
        sid_map[sid] = {"room_id": room_id, "user_id": "anonymous"}

    await sio.emit("room_state", room.model_dump(), room=sid)
    await sio.emit("room_state", room.model_dump(), room=room_id)


@sio.event
async def leave_session(sid, data) -> None:
    room_id = data.get("room_id")
    if room_id:
        sio.leave_room(sid, room_id)
        if sid in sid_map:
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
            await trigger_dj_voice(room_id, new_track)
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
            await sio.emit(
                "playback_toggled", {"is_playing": room.is_playing}, room=room_id
            )


@sio.event
async def skip_song(sid, data) -> None:
    room_id = data.get("room_id")
    if room_id in rooms:
        room = rooms[room_id]

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
            await sio.emit("room_state", room.model_dump(), room=room_id)
            await trigger_dj_voice(room_id, next_track)
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
