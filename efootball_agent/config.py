from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


@dataclass
class CaptureConfig:
    fps: float = 30.0
    region: dict[str, int] | None = None
    scrcpy_title: str = ""


@dataclass
class VisionConfig:
    blue_hsv_low: tuple[int, int, int] = (90, 55, 35)
    blue_hsv_high: tuple[int, int, int] = (140, 255, 255)
    min_player_area: int = 18
    confidence_threshold: float = 0.42


@dataclass
class TrackingConfig:
    lost_timeout: float = 0.35


@dataclass
class DecisionConfig:
    tick_rate: float = 10.0
    danger_threshold: float = 0.62
    tackle_distance: float = 0.11
    shoot_threshold: float = 0.70
    pass_threshold: float = 0.56
    dribble_threshold: float = 0.48
    state_confirm_frames: int = 3
    state_cooldown: float = 0.25


@dataclass
class ActionConfig:
    pass_duration: float = 0.08
    shoot_duration: float = 0.10
    tackle_cooldown: float = 0.65
    pass_cooldown: float = 0.35
    shoot_cooldown: float = 0.55
    dribble_change_cooldown: float = 0.55


@dataclass
class DebugConfig:
    overlay: bool = True
    show_frame: bool = False
    recording: bool = False
    recording_dir: str = "recordings"


@dataclass
class AppConfig:
    capture: CaptureConfig = field(default_factory=CaptureConfig)
    vision: VisionConfig = field(default_factory=VisionConfig)
    tracking: TrackingConfig = field(default_factory=TrackingConfig)
    decision: DecisionConfig = field(default_factory=DecisionConfig)
    action: ActionConfig = field(default_factory=ActionConfig)
    debug: DebugConfig = field(default_factory=DebugConfig)
    calibration: dict[str, Any] = field(default_factory=dict)


def _tuple(value: Any, default: tuple[int, int, int]) -> tuple[int, int, int]:
    if isinstance(value, (list, tuple)) and len(value) == 3:
        return tuple(int(x) for x in value)  # type: ignore[return-value]
    return default


def _read(path: str | Path) -> dict[str, Any]:
    if yaml is None:
        return {}
    file = Path(path)
    if not file.exists():
        return {}
    with file.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_config(default_path: str | Path, calibration_path: str | Path | None = None) -> AppConfig:
    raw = _read(default_path)
    capture = raw.get("capture", {})
    vision = raw.get("vision", {})
    tracking = raw.get("tracking", {})
    decision = raw.get("decision", {})
    action = raw.get("action", {})
    debug = raw.get("debug", {})
    cfg = AppConfig(
        capture=CaptureConfig(float(capture.get("fps", 30)), capture.get("region"), str(capture.get("scrcpy_title", ""))),
        vision=VisionConfig(_tuple(vision.get("blue_hsv_low"), VisionConfig.blue_hsv_low), _tuple(vision.get("blue_hsv_high"), VisionConfig.blue_hsv_high), int(vision.get("min_player_area", 18)), float(vision.get("confidence_threshold", 0.42))),
        tracking=TrackingConfig(float(tracking.get("lost_timeout", 0.35))),
        decision=DecisionConfig(float(decision.get("tick_rate", 10)), float(decision.get("danger_threshold", 0.62)), float(decision.get("tackle_distance", 0.11)), float(decision.get("shoot_threshold", 0.70)), float(decision.get("pass_threshold", 0.56)), float(decision.get("dribble_threshold", 0.48)), int(decision.get("state_confirm_frames", 3)), float(decision.get("state_cooldown", 0.25))),
        action=ActionConfig(float(action.get("pass_duration", 0.08)), float(action.get("shoot_duration", 0.10)), float(action.get("tackle_cooldown", 0.65)), float(action.get("pass_cooldown", 0.35)), float(action.get("shoot_cooldown", 0.55)), float(action.get("dribble_change_cooldown", 0.55))),
        debug=DebugConfig(bool(debug.get("overlay", True)), bool(debug.get("show_frame", False)), bool(debug.get("recording", False)), str(debug.get("recording_dir", "recordings"))),
    )
    if calibration_path:
        cfg.calibration = _read(calibration_path)
        if cfg.capture.region is None and isinstance(cfg.calibration.get("screen_region"), dict):
            cfg.capture.region = cfg.calibration["screen_region"]
    return cfg
