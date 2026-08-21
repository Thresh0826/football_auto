from __future__ import annotations

from abc import ABC, abstractmethod


class FrameSource(ABC):
    @abstractmethod
    def read(self): ...

    @abstractmethod
    def close(self) -> None: ...

