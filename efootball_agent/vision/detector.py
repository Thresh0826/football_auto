from __future__ import annotations

from dataclasses import dataclass

import numpy as np

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None


@dataclass
class Blob:
    center: tuple[float, float]
    area: float
    confidence: float


def find_color_blobs(frame: np.ndarray, hsv_low: tuple[int, int, int], hsv_high: tuple[int, int, int], min_area: int = 18) -> list[Blob]:
    if cv2 is None or frame is None or frame.size == 0:
        return []
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(hsv_low), np.array(hsv_high))
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    height, width = frame.shape[:2]
    output: list[Blob] = []
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue
        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            continue
        x = moments["m10"] / moments["m00"] / width
        y = moments["m01"] / moments["m00"] / height
        confidence = min(1.0, area / max(min_area * 8, 1))
        output.append(Blob((x, y), area, confidence))
    return output

