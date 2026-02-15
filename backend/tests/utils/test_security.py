from unittest.mock import patch

from app.utils.security import RateLimiter, check_authorization


def test_rate_limiter_allow():
    limiter = RateLimiter()
    # "skip_song": {"count": 1, "period": 10}

    assert limiter.check_rate_limit("sid1", "skip_song") is True

    # Second call immediately -> Fail
    assert limiter.check_rate_limit("sid1", "skip_song") is False


def test_rate_limiter_expiry():
    limiter = RateLimiter()
    # Mock time
    w_time = 1000.0

    with patch("time.time", return_value=w_time):
        assert limiter.check_rate_limit("sid1", "skip_song") is True

    # Advance time by 11 seconds (period is 10)
    with patch("time.time", return_value=w_time + 11.0):
        assert limiter.check_rate_limit("sid1", "skip_song") is True


def test_rate_limiter_unknown_event():
    limiter = RateLimiter()
    assert limiter.check_rate_limit("sid1", "unknown_event") is True


def test_check_authorization_success():
    sid_map = {"sid1": {"room_id": "room1", "user_id": "u1"}}
    assert check_authorization("sid1", "room1", sid_map) is True


def test_check_authorization_no_sid():
    sid_map = {}
    assert check_authorization("sid1", "room1", sid_map) is False


def test_check_authorization_wrong_room():
    sid_map = {"sid1": {"room_id": "room2", "user_id": "u1"}}
    assert check_authorization("sid1", "room1", sid_map) is False
