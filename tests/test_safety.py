from efootball_agent.action.action import ActionKind
from efootball_agent.decision.brain import Brain
from efootball_agent.state.game_state import GameState


def test_low_confidence_releases_inputs():
    decision = Brain().decide(GameState(timestamp=0.0, game_detected=False, confidence=0.0))
    assert decision.action.kind == ActionKind.RELEASE_ALL

