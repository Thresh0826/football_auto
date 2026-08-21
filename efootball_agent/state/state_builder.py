from __future__ import annotations

import time

from efootball_agent.state.enums import Phase, Possession
from efootball_agent.state.game_state import GameState, PlayerObservation


class StateBuilder:
    def build(self, *, ball_position=None, controlled_player_position=None, teammates=None, opponents=None, confidence=0.0, possession=Possession.UNKNOWN, phase=Phase.TRANSITION, **kwargs) -> GameState:
        return GameState(timestamp=time.time(), ball_position=ball_position, controlled_player_position=controlled_player_position, visible_teammates=teammates or [], visible_opponents=opponents or [], confidence=max(0.0, min(1.0, confidence)), possession=possession, phase=phase, **kwargs)

