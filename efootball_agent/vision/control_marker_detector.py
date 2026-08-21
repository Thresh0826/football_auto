from __future__ import annotations

from pathlib import Path

import numpy as np

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None


class ControlMarkerDetector:
    def __init__(self, template_path: str | None = None, threshold: float = 0.65) -> None:
        self.threshold = threshold
        self.template = None
        if template_path and cv2 is not None and Path(template_path).exists():
            self.template = cv2.imread(template_path, cv2.IMREAD_COLOR)

    def detect(self, frame: np.ndarray) -> tuple[tuple[float, float] | None, float]:
        if cv2 is None or self.template is None or frame is None:
            return None, 0.0
        result = cv2.matchTemplate(frame, self.template, cv2.TM_CCOEFF_NORMED)
        _, score, _, point = cv2.minMaxLoc(result)
        if score < self.threshold:
            return None, float(score)
        h, w = self.template.shape[:2]
        height, width = frame.shape[:2]
        return ((point[0] + w / 2) / width, (point[1] + h / 2) / height), float(score)

