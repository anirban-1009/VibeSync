from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SpotifyImage(BaseModel):
    url: str
    height: Optional[int] = None
    width: Optional[int] = None


class Track(BaseModel):
    uri: str
    name: str
    artist: str
    image: Optional[str] = None
    duration_ms: int
    uuid: Optional[str] = None
    added_by: Optional[str] = "system"
    added_by_name: Optional[str] = "System"
    added_by_image: Optional[str] = None


class VibeTrack(BaseModel):
    id: str  # Spotify ID for seeding
    name: str
    artist: str
    uri: str
    popularity: Optional[int] = None
    explicit: Optional[bool] = False
    album: Optional[str] = None


class UserVibeData(BaseModel):
    top_tracks: List[VibeTrack] = []
    top_artists: List[dict] = []  # Can refine this later if we fetch artists explicitly


class RoomVibeProfile(BaseModel):
    users_data: Dict[str, UserVibeData] = Field(default_factory=dict)
    room_aggregate: Dict[str, float] = Field(default_factory=dict)


class RoomUser(BaseModel):
    id: str
    name: Optional[str] = None
    image: Optional[str] = None


class RoomState(BaseModel):
    current_track: Optional[Track] = None
    queue: List[Track] = Field(default_factory=list)
    history: List[Track] = Field(default_factory=list)
    is_playing: bool = False
    users: List[RoomUser] = Field(default_factory=list)
    vibe_profile: RoomVibeProfile = Field(default_factory=RoomVibeProfile)
    ai_mode_enabled: bool = True
