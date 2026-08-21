from efootball_agent.action.action import Action, ActionKind
from efootball_agent.action.planner import ActionPlanner
from efootball_agent.input_layer.dry_run import DryRunInputBackend


def calibration():
    return {"joystick_center": {"x": 100, "y": 500}, "joystick_radius": 70, "pass_button": {"x": 900, "y": 400}, "shoot_button": {"x": 1000, "y": 350}}


def test_joystick_and_release():
    backend = DryRunInputBackend()
    planner = ActionPlanner(backend, calibration())
    planner.execute(Action(ActionKind.MOVE, direction=(1, 0), intensity=0.5, duration=0.01))
    planner.release_all()
    assert ("down", "left") in backend.events
    assert ("release_all", None) in backend.events


def test_special_buttons_are_mapped():
    backend = DryRunInputBackend()
    cfg = calibration() | {"pass_swipe_end": {"x": 800, "y": 300}, "through_button": {"x": 850, "y": 400}, "through_swipe_end": {"x": 850, "y": 300}, "clear_button": {"x": 950, "y": 400}}
    planner = ActionPlanner(backend, cfg)
    for kind in (ActionKind.LOB_PASS, ActionKind.THROUGH_PASS, ActionKind.FLY_THROUGH, ActionKind.CLEAR):
        planner.execute(Action(kind, duration=0.01))
    assert sum(1 for event in backend.events if event[0] == "down") == 8


def test_kick_primes_last_joystick_direction_before_button():
    backend = DryRunInputBackend()
    planner = ActionPlanner(backend, calibration())
    planner.execute(Action(ActionKind.SHOOT, direction=(1, 0), duration=0.01))
    moves = [event for event in backend.events if event[0] == "move_to"]
    downs = [event for event in backend.events if event[0] == "down"]
    assert moves[0][1] == (100, 500)
    assert moves[1][1] == (152, 500)
    assert downs == [("down", "left"), ("down", "left")]
