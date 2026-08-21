from __future__ import annotations

from .geometry import field_zone


class FieldDetector:
    def zone(self, normalized_point: tuple[float, float]) -> str:
        return field_zone(normalized_point)

