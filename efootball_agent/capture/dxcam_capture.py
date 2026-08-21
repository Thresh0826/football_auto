from __future__ import annotations

from typing import Any

from .base import FrameSource


class DxcamCapture(FrameSource):
    """采集 scrcpy 窗口所在的桌面区域；region 使用 left/top/right/bottom。"""

    def __init__(self, region: dict[str, int] | None = None, fps: float = 30.0) -> None:
        try:
            import dxcam
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("未安装 dxcam，请执行 pip install -r requirements.txt") from exc
        self.camera = dxcam.create(output_color="BGR")
        self.region = None
        if region:
            self.region = (region["left"], region["top"], region["right"], region["bottom"])
        self.camera.start(region=self.region, target_fps=int(fps), video_mode=True)

    def read(self):
        return self.camera.get_latest_frame()

    def close(self) -> None:
        self.camera.stop()

