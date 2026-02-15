import time
from collections import defaultdict

from app.utils.logger import logger


class RateLimiter:
    def __init__(self):
        # Maps event_name -> sid -> list of timestamps
        self.limits = {
            "add_to_queue": {"count": 5, "period": 60},  # 5 songs per min
            "skip_song": {"count": 1, "period": 10},  # 1 skip per 10s
            "set_vibe": {"count": 1, "period": 30},  # 1 vibe per 30s
            "set_repeat_mode": {"count": 5, "period": 10},  # Spammable UI
            "set_volume": {"count": 10, "period": 5},  # Volume slider can be noisy
        }
        self.tracking = defaultdict(lambda: defaultdict(list))

    def check_rate_limit(self, sid: str, event_name: str) -> bool:
        """
        Returns True if allowed, False if limit exceeded.
        """
        if event_name not in self.limits:
            return True

        config = self.limits[event_name]
        limit_count = config["count"]
        period = config["period"]

        now = time.time()

        # Get history for this sid/event
        history = self.tracking[event_name][sid]

        # Clean up old timestamps
        history = [t for t in history if now - t < period]
        self.tracking[event_name][sid] = history

        if len(history) >= limit_count:
            logger.warning(f"Rate limit exceeded for {sid} on {event_name}")
            return False

        # Add new timestamp
        history.append(now)
        self.tracking[event_name][sid] = history
        return True


# Global instance
rate_limiter = RateLimiter()


def check_authorization(sid: str, room_id: str, sid_map: dict) -> bool:
    """
    Verifies that the socket ID is actually a member of the requested room.
    """
    if sid not in sid_map:
        return False

    user_info = sid_map[sid]
    if user_info.get("room_id") != room_id:
        logger.warning(
            f"Authorization failed: {sid} attempted action on {room_id} but is in {user_info.get('room_id')}"
        )
        return False

    return True
