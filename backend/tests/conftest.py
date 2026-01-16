import os
import sys

import pytest

# Add the backend directory to sys.path so 'app' can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_room_state():
    from app.utils.models import RoomState

    return RoomState()
