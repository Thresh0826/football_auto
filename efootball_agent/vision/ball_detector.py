from __future__ import annotations

from dataclasses import dataclass

import numpy as np

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None


@dataclass
class BallObservation:
    position: tuple[float, float] | None
    confidence: float
    predicted: bool = False


class BallDetector:
    def __init__(self, lost_timeout: float = 0.35) -> None:
        self.lost_timeout = lost_timeout
        self.last: BallObservation | None = None
        self.last_time = 0.0

    def detect(self, frame: np.ndarray, now: float) -> BallObservation:
        candidate = self._candidate(frame)
        if candidate.position is not None:
            self.last, self.last_time = candidate, now
            return candidate
        if self.last and now - self.last_time <= self.lost_timeout:
            return BallObservation(self.last.position, self.last.confidence * 0.65, True)
        return BallObservation(None, 0.0)

    def _candidate(self, frame: np.ndarray) -> BallObservation:
        if cv2 is None or frame is None or frame.size == 0:
            return BallObservation(None, 0.0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # 足球候选：高亮、低饱和小连通域；最终阈值由实际画面校准。
        mask = cv2.inRange(hsv, np.array((0, 0, 145)), np.array((180, 110, 255)))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        height, width = frame.shape[:2]
        options = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 4 <= area <= max(80, width * height * 0.00025):
                moments = cv2.moments(contour)
                if moments["m00"]:
                    options.append((area, moments["m10"] / moments["m00"] / width, moments["m01"] / moments["m00"] / height))
        if not options:
            return BallObservation(None, 0.0)
        area, x, y = max(options, key=lambda item: item[0])
        return BallObservation((x, y), min(0.85, 0.35 + area / 80.0))

