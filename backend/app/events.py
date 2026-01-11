import uuid

from app.server import sio
from app.state import rooms, sid_map


@sio.event
async def connect(sid, environ):
    pass


@sio.event
async def disconnect(sid):
    if sid in sid_map:
        user_info = sid_map[sid]
        room_id = user_info.get("room_id")
        user_id = user_info.get("user_id")

        if room_id and room_id in rooms:
            rooms[room_id]["users"] = [
                u for u in rooms[room_id]["users"] if u["id"] != user_id
            ]
            await sio.emit("room_state", rooms[room_id], room=room_id)

        del sid_map[sid]


@sio.event
async def join_room(sid, data):
    room_id = data.get("room_id")
    user_profile = data.get("user_profile")

    if not room_id:
        return

    await sio.enter_room(sid, room_id)

    # Init room if not exists
    if room_id not in rooms:
        rooms[room_id] = {
            "current_track": None,
            "queue": [],
            "history": [],
            "is_playing": False,
            "users": [],
        }

    # Store user info
    if user_profile:
        user = {
            "id": user_profile.get("id"),
            "name": user_profile.get("display_name"),
            "image": user_profile.get("images", [{}])[0].get("url")
            if user_profile.get("images")
            else None,
        }
        # Avoid duplicates
        existing = [u for u in rooms[room_id]["users"] if u["id"] != user["id"]]
        existing.append(user)
        rooms[room_id]["users"] = existing

        sid_map[sid] = {"room_id": room_id, "user_id": user["id"]}
    else:
        sid_map[sid] = {"room_id": room_id, "user_id": "anonymous"}

    # Send current state
    await sio.emit("room_state", rooms[room_id], room=sid)
    # Broadcast update
    await sio.emit("room_state", rooms[room_id], room=room_id)


@sio.event
async def leave_session(sid, data):
    room_id = data.get("room_id")
    if room_id:
        sio.leave_room(sid, room_id)
        if sid in sid_map:
            # Logic similar to disconnect if needed, or just remove from map
            # usually disconnect handles the cleanup
            pass


@sio.event
async def add_to_queue(sid, data):
    """
    Data: { room_id, track: { uri, name, artist, image, duration_ms } }
    """
    room_id = data.get("room_id")
    track = data.get("track")

    session = sid_map.get(sid, {})
    user_id = session.get("user_id", "anonymous")

    if room_id and track and room_id in rooms:
        room = rooms[room_id]

        track["uuid"] = str(uuid.uuid4())
        track["added_by"] = user_id

        if room["current_track"] is None:
            room["current_track"] = track
            room["is_playing"] = True
            await sio.emit("play_track", track, room=room_id)
            await sio.emit("room_state", room, room=room_id)
        else:
            room["queue"].append(track)
            await sio.emit("queue_updated", room["queue"], room=room_id)


@sio.event
async def toggle_playback(sid, data):
    room_id = data.get("room_id")
    if room_id in rooms:
        room = rooms[room_id]
        if room["current_track"]:
            room["is_playing"] = not room["is_playing"]
            # Broadcast to all explicitly
            await sio.emit(
                "playback_toggled", {"is_playing": room["is_playing"]}, room=room_id
            )


@sio.event
async def skip_song(sid, data):
    room_id = data.get("room_id")
    if room_id in rooms:
        room = rooms[room_id]

        # Add current to history if it exists
        if room["current_track"]:
            room["history"].insert(0, room["current_track"])
            # Keep history size manageable
            if len(room["history"]) > 20:
                room["history"].pop()

        if len(room["queue"]) > 0:
            next_track = room["queue"].pop(0)
            room["current_track"] = next_track
            room["is_playing"] = True
            await sio.emit("play_track", next_track, room=room_id)
            await sio.emit("room_state", room, room=room_id)  # Sync history/queue
        else:
            room["current_track"] = None
            room["is_playing"] = False
            await sio.emit("stop_player", room=room_id)
            await sio.emit("room_state", room, room=room_id)


@sio.event
async def remove_from_queue(sid, data):
    room_id = data.get("room_id")
    track_uuid = data.get("track_uuid")

    if room_id in rooms and track_uuid:
        room = rooms[room_id]
        original_len = len(room["queue"])
        room["queue"] = [t for t in room["queue"] if t.get("uuid") != track_uuid]

        if len(room["queue"]) != original_len:
            await sio.emit("queue_updated", room["queue"], room=room_id)
