from __future__ import annotations

from efootball_agent.state.game_state import GameState, PassingOpportunity


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def score_pass(state: GameState) -> float:
    if not state.passing_opportunities:
        return 0.0
    best = max(state.passing_opportunities, key=lambda item: item.score)
    return clamp(0.45 * best.score + 0.25 * best.lane_clear + 0.20 * (1.0 - best.pressure) + 0.10 * min(1.0, 1.0 / max(0.2, best.distance)))


def best_pass(state: GameState) -> PassingOpportunity | None:
    return max(state.passing_opportunities, key=lambda item: item.score, default=None)


def score_shoot(state: GameState) -> float:
    return clamp(state.shooting_opportunity * 0.65 + (1.0 - state.pressure_level) * 0.15 + (1.0 - state.nearest_opponent_distance) * 0.05 + (1.0 if state.field_zone == "PENALTY_AREA" else 0.0) * 0.15)


def score_dribble(state: GameState) -> float:
    return clamp(state.dribble_space * 0.65 + (1.0 - state.pressure_level) * 0.25 + (1.0 - state.nearest_opponent_distance) * 0.10)


def score_defensive_press(state: GameState) -> float:
    return clamp(state.danger_level * 0.55 + (1.0 - state.nearest_opponent_distance) * 0.35 + state.confidence * 0.10)


def score_tackle(state: GameState) -> float:
    if state.nearest_opponent_distance > 0.14:
        return 0.0
    return clamp(state.danger_level * 0.60 + (1.0 - state.nearest_opponent_distance / 0.14) * 0.30 + state.confidence * 0.10)

