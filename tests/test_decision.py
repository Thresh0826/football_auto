from efootball_agent.decision.brain import Brain
from efootball_agent.state.enums import AgentState
from efootball_agent.vision.mock_provider import MockVisionProvider


def stable(brain, state):
    result = None
    for _ in range(3):
        result = brain.decide(state)
    return result


def test_attack_cases():
    provider = MockVisionProvider()
    assert stable(Brain(), provider.case("dribble")).action.kind.value == "SPRINT"
    assert stable(Brain(), provider.case("pass")).action.kind.value == "PASS"
    assert stable(Brain(), provider.case("shoot")).action.kind.value == "SHOOT"


def test_defense_cases():
    provider = MockVisionProvider()
    normal = stable(Brain(), provider.case("defense"))
    danger = stable(Brain(), provider.case("danger"))
    assert normal.state == AgentState.DEFEND_NORMAL
    assert normal.action.kind.value in {"MOVE", "PRESS"}
    assert danger.state == AgentState.DEFEND_DANGER
    assert danger.action.kind.value in {"PRESS", "TACKLE"}


def test_receiving_state():
    result = stable(Brain(), MockVisionProvider().case("receiving"))
    assert result.state == AgentState.RECEIVING


def test_goalkeeper_and_emergency_clear():
    provider = MockVisionProvider()
    keeper = provider.case("shoot")
    keeper.metadata["goalkeeper_has_ball"] = True
    result = stable(Brain(), keeper)
    assert result.action.kind.value == "CLEAR"
