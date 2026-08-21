from __future__ import annotations

from abc import ABC, abstractmethod


class InputBackend(ABC):
    @abstractmethod
    def move_to(self, x: int, y: int) -> None: ...

    @abstractmethod
    def button_down(self, button: str = "left") -> None: ...

    @abstractmethod
    def button_up(self, button: str = "left") -> None: ...

    @abstractmethod
    def release_all(self) -> None: ...

