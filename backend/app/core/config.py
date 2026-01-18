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
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")

        # LLM Settings
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama2")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-pro")

    @classmethod
    def get_settings(cls) -> "Settings":
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
            validate_environment_settings(cls._instance)
        return cls._instance
