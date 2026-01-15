# Global in-memory state
# In a real app, use Redis or a DB

rooms = {}
# Structure:
# rooms[room_id] = {
#     "current_track": None,
#     "queue": [],
#     "history": [],
#     "is_playing": False,
#     "users": [],
#     "vibe_profile": {
#         "users_data": {},  # { user_id: { top_tracks: [], top_artists: [] } }
#         "room_aggregate": {}
#     },
#     "ai_mode_enabled": True
# }

# Map socket_id -> user info
sid_map = {}
