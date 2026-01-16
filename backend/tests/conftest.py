import os
import sys

import pytest

# Set dummy env vars for testing BEFORE importing app modules to avoid config validation errors
os.environ.setdefault("CLIENT_ID", "test_client_id")
os.environ.setdefault("CLIENT_SECRET", "test_client_secret")
os.environ.setdefault("REDIRECT_URI", "http://localhost/callback")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")

# Add the backend directory to sys.path so 'app' can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_room_state():
    from app.utils.models import RoomState

    return RoomState()
