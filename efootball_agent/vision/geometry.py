from __future__ import annotations

import math


def normalize_point(point: tuple[float, float], width: float, height: float) -> tuple[float, float]:
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    return max(0.0, min(1.0, point[0] / width)), max(0.0, min(1.0, point[1] / height))


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def direction(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy) or 1.0
    return dx / length, dy / length


def field_zone(point: tuple[float, float]) -> str:
    x, y = point
    if not (0 <= x <= 1 and 0 <= y <= 1):
        return "UNKNOWN"
    if x >= 0.84:
        return "PENALTY_AREA"
    if x >= 0.67:
        return "ATTACKING_THIRD"
    if x <= 0.16:
        return "OWN_PENALTY_AREA"
    if x <= 0.33:
        return "DEFENSIVE_THIRD"
    return "MIDFIELD"


def danger_zone(opponent: tuple[float, float], goal_x: float = 0.0) -> bool:
    x, y = opponent
    return (x <= 0.20 if goal_x == 0.0 else x >= 0.80) and 0.18 <= y <= 0.82

