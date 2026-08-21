from __future__ import annotations

import math
import time
from typing import Any

from efootball_agent.action.action import Action, ActionKind
from efootball_agent.input_layer.base import InputBackend


class ActionPlanner:
    def __init__(self, backend: InputBackend, calibration: dict[str, Any]) -> None:
        self.backend = backend
        self.calibration = calibration
        self.joystick_down = False
        self.held_button: str | None = None

    def _point(self, name: str) -> tuple[int, int] | None:
        value = self.calibration.get(name)
        if isinstance(value, dict) and "x" in value and "y" in value:
            return int(value["x"]), int(value["y"])
        if isinstance(value, (list, tuple)) and len(value) == 2:
            return int(value[0]), int(value[1])
        return None

    def _joystick_target(self, direction: tuple[float, float], intensity: float) -> tuple[int, int] | None:
        center = self._point("joystick_center")
        radius = float(self.calibration.get("joystick_radius", 0))
        if not center or radius <= 0:
            return None
        dx, dy = direction
        length = math.hypot(dx, dy) or 1.0
        scale = min(1.0, max(0.0, intensity)) * radius / length
        return round(center[0] + dx * scale), round(center[1] + dy * scale)

    def _joystick(self, direction: tuple[float, float], intensity: float, duration: float) -> None:
        target = self._joystick_target(direction, intensity)
        center = self._point("joystick_center")
        if not target or not center:
            return
        self.backend.move_to(*center)
        if not self.joystick_down:
            self.backend.button_down()
            self.joystick_down = True
        self.backend.move_to(*target)
        if duration > 0:
            time.sleep(min(duration, 0.8))

    def _tap(self, name: str, duration: float = 0.06) -> None:
        point = self._point(name)
        if not point:
            return
        self.backend.move_to(*point)
        self.backend.button_down()
        time.sleep(min(max(duration, 0.01), 0.8))
        self.backend.button_up()

    def _swipe(self, start_name: str, end_name: str, duration: float = 0.18) -> None:
        start = self._point(start_name)
        end = self._point(end_name)
        if not start or not end:
            return
        self.backend.move_to(*start)
        self.backend.button_down()
        time.sleep(0.03)
        self.backend.move_to(*end)
        time.sleep(min(max(duration, 0.05), 0.8))
        self.backend.button_up()

    def _prime_direction(self, direction: tuple[float, float], intensity: float = 0.75) -> None:
        """输入一次方向并释放；游戏会把它作为下一次踢球动作的方向。"""
        self._release_joystick()
        target = self._joystick_target(direction, intensity)
        center = self._point("joystick_center")
        if not target or not center:
            return
        self.backend.move_to(*center)
        self.backend.button_down()
        self.backend.move_to(*target)
        time.sleep(0.04)
        self.backend.button_up()

    def _release_joystick(self) -> None:
        if self.joystick_down:
            self.backend.button_up()
            self.joystick_down = False

    def execute(self, action: Action) -> None:
        if action.kind == ActionKind.RELEASE_ALL:
            self.release_all()
            return
        if action.kind in (ActionKind.MOVE, ActionKind.SPRINT, ActionKind.PRESS):
            if action.kind == ActionKind.PRESS:
                point = self._point("pressure_button")
                if point:
                    self.backend.move_to(*point)
                    if not self.held_button:
                        self.backend.button_down()
                        self.held_button = "pressure_button"
                self._joystick(action.direction, action.intensity, action.duration)
            else:
                self._joystick(action.direction, action.intensity, action.duration)
                if action.kind == ActionKind.SPRINT:
                    self._tap("sprint_button", min(action.duration, 0.4))
            return
        if action.kind == ActionKind.PASS:
            self._prime_direction(action.direction)
            self._tap("pass_button", action.duration)
        elif action.kind == ActionKind.LOB_PASS:
            self._prime_direction(action.direction)
            self._swipe("pass_button", "pass_swipe_end", action.duration)
        elif action.kind == ActionKind.THROUGH_PASS:
            self._prime_direction(action.direction)
            self._tap("through_button", action.duration)
        elif action.kind == ActionKind.FLY_THROUGH:
            self._prime_direction(action.direction)
            self._swipe("through_button", "through_swipe_end", action.duration)
        elif action.kind == ActionKind.SHOOT:
            self._prime_direction(action.direction)
            self._tap("shoot_button", action.duration)
        elif action.kind == ActionKind.CLEAR:
            self._prime_direction(action.direction)
            self._tap("clear_button", action.duration)
        elif action.kind == ActionKind.TACKLE:
            self._tap("tackle_button", action.duration)
        elif action.kind == ActionKind.WAIT:
            time.sleep(min(max(action.duration, 0.0), 0.8))

    def release_all(self) -> None:
        self._release_joystick()
        if self.held_button:
            self.backend.button_up()
            self.held_button = None
        self.backend.release_all()
