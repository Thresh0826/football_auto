from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ActionKind(str, Enum):
    MOVE = "MOVE"
    SPRINT = "SPRINT"
    PASS = "PASS"
    LOB_PASS = "LOB_PASS"
    THROUGH_PASS = "THROUGH_PASS"
    FLY_THROUGH = "FLY_THROUGH"
    SHOOT = "SHOOT"
    CLEAR = "CLEAR"
    PRESS = "PRESS"
    TACKLE = "TACKLE"
    RELEASE_ALL = "RELEASE_ALL"
    WAIT = "WAIT"


@dataclass
class Action:
    kind: ActionKind
    direction: tuple[float, float] = (0.0, 0.0)
    intensity: float = 0.0
    power: float = 0.0
    duration: float = 0.0
    reason: str = ""
