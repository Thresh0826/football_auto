from __future__ import annotations

import numpy as np

from .detector import Blob, find_color_blobs


class PlayerDetector:
    def __init__(self, blue_low=(90, 55, 35), blue_high=(140, 255, 255), min_area=18) -> None:
        self.blue_low = tuple(blue_low)
        self.blue_high = tuple(blue_high)
        self.min_area = min_area

    def detect_our_team(self, frame: np.ndarray) -> list[Blob]:
        return find_color_blobs(frame, self.blue_low, self.blue_high, self.min_area)

    def detect_opponents(self, frame: np.ndarray, our_team: list[Blob]) -> list[Blob]:
        # 对方颜色不固定，V1 保留中性候选接口；实际使用时由模板/颜色配置补充。
        return []

