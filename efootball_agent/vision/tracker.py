from __future__ import annotations

import math


class NearestNeighborTracker:
    def __init__(self, max_distance: float = 0.12) -> None:
        self.max_distance = max_distance
        self.previous: list[tuple[float, float]] = []

    def update(self, points: list[tuple[float, float]]) -> list[tuple[float, float]]:
        if not self.previous:
            self.previous = list(points)
            return list(points)
        accepted: list[tuple[float, float]] = []
        for point in points:
            if any(math.dist(point, old) <= self.max_distance for old in self.previous):
                accepted.append(point)
        self.previous = list(points)
        return accepted

