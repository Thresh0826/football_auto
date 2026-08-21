from __future__ import annotations

import time


class Cooldown:
    def __init__(self) -> None:
        self._until: dict[str, float] = {}

    def ready(self, key: str, now: float | None = None) -> bool:
        return (now or time.monotonic()) >= self._until.get(key, 0.0)

    def trigger(self, key: str, seconds: float, now: float | None = None) -> None:
        self._until[key] = (now or time.monotonic()) + max(0.0, seconds)

