from __future__ import annotations

from .base import InputBackend


class DryRunInputBackend(InputBackend):
    def __init__(self) -> None:
        self.events: list[tuple[str, object]] = []

    def move_to(self, x: int, y: int) -> None:
        self.events.append(("move_to", (x, y)))

    def button_down(self, button: str = "left") -> None:
        self.events.append(("down", button))

    def button_up(self, button: str = "left") -> None:
        self.events.append(("up", button))

    def release_all(self) -> None:
        self.events.append(("release_all", None))

