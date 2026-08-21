from __future__ import annotations

import time


class RateLimiter:
    def __init__(self, interval: float) -> None:
        self.interval = max(0.0, interval)
        self.last = 0.0

    def ready(self, now: float | None = None) -> bool:
        current = now if now is not None else time.monotonic()
        if current - self.last < self.interval:
            return False
        self.last = current
        return True

