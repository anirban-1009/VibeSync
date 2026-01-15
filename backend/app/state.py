from typing import Dict

from app.utils.models import RoomState

# Global in-memory state
# In a real app, use Redis or a DB

rooms: Dict[str, RoomState] = {}

# Map socket_id -> user info
sid_map = {}
