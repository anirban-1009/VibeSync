import os

from app.utils.exceptions import validate_environment_settings
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.redirect_uri = os.getenv("REDIRECT_URI")
        self.frontend_url = os.getenv("FRONTEND_URL")

    @classmethod
    def get_settings(cls) -> "Settings":
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
            validate_environment_settings(cls._instance)
        return cls._instance
