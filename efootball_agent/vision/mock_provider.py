from __future__ import annotations

import time

from efootball_agent.config import CaptureConfig
from efootball_agent.state.enums import Phase, Possession
from efootball_agent.state.game_state import GameState, PassingOpportunity, PlayerObservation
from .live_provider import LiveVisionProvider


class MockVisionProvider:
    def __init__(self) -> None:
        self._case = "dribble"

    @classmethod
    def live_from_scrcpy(cls, config: CaptureConfig) -> "MockVisionProvider":
        # 保留旧工厂名，app.py 会优先使用 LiveVisionProvider。
        return cls()

    def case(self, name: str) -> GameState:
        base = dict(timestamp=time.time(), game_detected=True, confidence=0.95, controlled_player_position=(0.45, 0.50), ball_position=(0.47, 0.50), goal_direction=(1.0, 0.0))
        if name == "dribble":
            return GameState(**base, possession=Possession.OUR_TEAM, phase=Phase.ATTACK, field_zone="MIDFIELD", nearest_opponent_distance=0.42, pressure_level=0.20, shooting_opportunity=0.20, dribble_space=0.90)
        if name == "pass":
            return GameState(**base, possession=Possession.OUR_TEAM, phase=Phase.ATTACK, field_zone="MIDFIELD", nearest_opponent_distance=0.08, pressure_level=0.85, shooting_opportunity=0.12, dribble_space=0.15, passing_opportunities=[PassingOpportunity((0.67, 0.40), 0.90, 0.23, 0.92, 0.10, True)])
        if name == "shoot":
            return GameState(**base, possession=Possession.OUR_TEAM, phase=Phase.ATTACK, field_zone="PENALTY_AREA", nearest_opponent_distance=0.22, pressure_level=0.20, shooting_opportunity=0.98, dribble_space=0.30)
        if name == "defense":
            return GameState(**base, possession=Possession.OPPONENT, phase=Phase.DEFENSE, field_zone="MIDFIELD", nearest_opponent_distance=0.30, pressure_level=0.20, danger_level=0.20, metadata={"defensive_direction": (0.2, 0.0)})
        if name == "danger":
            return GameState(**base, possession=Possession.OPPONENT, phase=Phase.DEFENSE, field_zone="OWN_PENALTY_AREA", nearest_opponent_distance=0.06, pressure_level=0.75, danger_level=0.95, metadata={"defensive_direction": (-0.7, 0.0)})
        if name == "receiving":
            return GameState(**base, possession=Possession.LOOSE, phase=Phase.TRANSITION, receiving=True, controlled_player_changed=True, pressure_level=0.35)
        return GameState(**base)

    def next(self):
        return None, self.case(self._case)
