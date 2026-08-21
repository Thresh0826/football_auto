from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .enums import AgentState, Phase, Possession

Point = tuple[float, float]


@dataclass
class PlayerObservation:
    position: Point
    confidence: float = 1.0
    player_id: str | None = None


@dataclass
class PassingOpportunity:
    target: Point
    score: float
    distance: float
    lane_clear: float
    pressure: float
    is_user_player: bool = False
    pass_type: str = "PASS"


@dataclass
class GameState:
    timestamp: float
    game_detected: bool = True
    possession: Possession = Possession.UNKNOWN
    phase: Phase = Phase.TRANSITION
    agent_state: AgentState = AgentState.IDLE
    controlled_player_position: Point | None = None
    ball_position: Point | None = None
    goal_direction: Point = (1.0, 0.0)
    field_zone: str = "UNKNOWN"
    nearest_opponent_position: Point | None = None
    nearest_opponent_distance: float = 1.0
    visible_teammates: list[PlayerObservation] = field(default_factory=list)
    visible_opponents: list[PlayerObservation] = field(default_factory=list)
    ball_distance_to_controlled_player: float = 1.0
    pressure_level: float = 0.0
    shooting_opportunity: float = 0.0
    passing_opportunities: list[PassingOpportunity] = field(default_factory=list)
    dribble_space: float = 0.0
    danger_level: float = 0.0
    confidence: float = 0.0
    receiving: bool = False
    controlled_player_changed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
