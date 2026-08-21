from __future__ import annotations

import ctypes
import sys

from .base import InputBackend


class Win32InputBackend(InputBackend):
    """普通 Windows 鼠标输入；仅用于 scrcpy 镜像窗口中的虚拟按键。"""

    def __init__(self, window_title: str = "") -> None:
        if sys.platform != "win32":
            raise RuntimeError("Win32InputBackend 只能在 Windows 使用")
        self.user32 = ctypes.windll.user32
        self.window_title = window_title
        self._down: set[str] = set()

    def _focus_target(self) -> None:
        if not self.window_title:
            return
        hwnd = self.user32.FindWindowW(None, self.window_title)
        if hwnd:
            self.user32.ShowWindow(hwnd, 9)
            self.user32.SetForegroundWindow(hwnd)

    def move_to(self, x: int, y: int) -> None:
        self._focus_target()
        self.user32.SetCursorPos(int(x), int(y))

    def button_down(self, button: str = "left") -> None:
        flag = 0x0002 if button == "left" else 0x0008
        self.user32.mouse_event(flag, 0, 0, 0, 0)
        self._down.add(button)

    def button_up(self, button: str = "left") -> None:
        flag = 0x0004 if button == "left" else 0x0010
        self.user32.mouse_event(flag, 0, 0, 0, 0)
        self._down.discard(button)

    def release_all(self) -> None:
        for button in tuple(self._down):
            self.button_up(button)
        self._down.clear()
