import urllib.parse

from app.core.config import Settings
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from spotipy.oauth2 import SpotifyOAuth

settings = Settings.get_settings()

router = APIRouter()

CLIENT_ID = settings.client_id
CLIENT_SECRET = settings.client_secret
REDIRECT_URI = settings.redirect_uri
FRONTEND_URL = settings.frontend_url

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="streaming user-read-email user-read-private user-modify-playback-state user-top-read",
)


@router.get("/login")
async def login() -> RedirectResponse:
    auth_url = sp_oauth.get_authorize_url()
    return RedirectResponse(auth_url)


@router.get("/callback")
async def callback(code: str) -> RedirectResponse:
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info["access_token"]
    _refresh_token = token_info["refresh_token"]

    # Redirect back to frontend with token
    params = urllib.parse.urlencode({"token": access_token})
    return RedirectResponse(f"{FRONTEND_URL}?{params}")
