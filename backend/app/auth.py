import os
import urllib.parse

from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from spotipy.oauth2 import SpotifyOAuth

router = APIRouter()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://127.0.0.1:8000/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="streaming user-read-email user-read-private user-modify-playback-state",
)


@router.get("/login")
async def login():
    auth_url = sp_oauth.get_authorize_url()
    return RedirectResponse(auth_url)


@router.get("/callback")
async def callback(code: str):
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info["access_token"]
    refresh_token = token_info["refresh_token"]

    # Redirect back to frontend with token
    params = urllib.parse.urlencode({"token": access_token})
    return RedirectResponse(f"{FRONTEND_URL}?{params}")
