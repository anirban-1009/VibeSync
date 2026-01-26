import urllib.parse

from app.core.config import Settings
from app.utils.logger import logger
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from spotipy.cache_handler import CacheHandler
from spotipy.oauth2 import SpotifyOAuth

settings = Settings.get_settings()

router = APIRouter()

CLIENT_ID = settings.client_id
CLIENT_SECRET = settings.client_secret
REDIRECT_URI = settings.redirect_uri
FRONTEND_URL = settings.frontend_url


class NoCacheHandler(CacheHandler):
    """
    A cache handler that does nothing.
    Used to prevent server-side caching of user tokens in the global SpotifyOAuth instance.
    """

    def get_cached_token(self):
        return None

    def save_token_to_cache(self, token_info):
        pass


sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="streaming user-read-email user-read-private user-modify-playback-state user-read-playback-state user-read-currently-playing user-top-read",
    show_dialog=True,
    cache_handler=NoCacheHandler(),
)


@router.get("/login")
async def login() -> RedirectResponse:
    auth_url = sp_oauth.get_authorize_url()
    logger.info(f"Login requested. Redirecting to Spotify. URI: {REDIRECT_URI}")
    return RedirectResponse(auth_url)


@router.get("/callback")
async def callback(code: str) -> RedirectResponse:
    logger.info(f"Callback received. Code: {code[:10]}... URI: {REDIRECT_URI}")
    try:
        token_info = sp_oauth.get_access_token(code, check_cache=False)
    except Exception as e:
        import traceback

        logger.error(f"Error exchanging token: {e}")
        logger.error(traceback.format_exc())
        return RedirectResponse(
            f"{FRONTEND_URL}?error=token_exchange_failed&details={str(e)}"
        )

    access_token = token_info["access_token"]
    _refresh_token = token_info["refresh_token"]

    # Redirect back to frontend with token
    params = urllib.parse.urlencode({"token": access_token})
    return RedirectResponse(f"{FRONTEND_URL}?{params}")
