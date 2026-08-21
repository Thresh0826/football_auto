from __future__ import annotations

import time

import numpy as np

from efootball_agent.capture.dxcam_capture import DxcamCapture
from efootball_agent.config import CaptureConfig, VisionConfig
from efootball_agent.state.enums import Phase, Possession
from efootball_agent.state.game_state import GameState, PlayerObservation, PassingOpportunity
from .ball_detector import BallDetector
from .control_marker_detector import ControlMarkerDetector
from .detector import find_color_blobs
from .geometry import distance, field_zone


class LiveVisionProvider:
    """从 scrcpy 窗口所在桌面区域读取画面。

    视觉证据不完整时返回低置信度 GameState，由 Brain 释放所有输入。
    这比根据不确定画面猜测动作更安全。
    """

    def __init__(self, capture: DxcamCapture, vision: VisionConfig, calibration: dict | None = None) -> None:
        self.capture = capture
        self.vision = vision
        calibration = calibration or {}
        template_path = calibration.get("control_marker_template")
        self.marker = ControlMarkerDetector(template_path if isinstance(template_path, str) else None)
        self.ball = BallDetector()
        self.last_controlled: tuple[float, float] | None = None

    @classmethod
    def create(cls, capture_config: CaptureConfig, vision_config: VisionConfig, calibration: dict | None = None) -> "LiveVisionProvider":
        return cls(DxcamCapture(capture_config.region, capture_config.fps), vision_config, calibration)

    def next(self):
        frame = self.capture.read()
        if frame is None:
            return None, self._unknown()
        blobs = find_color_blobs(frame, self.vision.blue_hsv_low, self.vision.blue_hsv_high, self.vision.min_player_area)
        teammates = [PlayerObservation(blob.center, blob.confidence) for blob in blobs]
        ball = self.ball.detect(frame, time.time())
        marker_position, marker_confidence = self.marker.detect(frame)
        controlled = None
        controlled_confidence = 0.0
        if marker_position and teammates:
            controlled = min(teammates, key=lambda player: distance(player.position, marker_position)).position
            controlled_confidence = marker_confidence
        changed = controlled is not None and (self.last_controlled is None or distance(controlled, self.last_controlled) > 0.08)
        if controlled is not None:
            self.last_controlled = controlled
        ball_distance = distance(controlled, ball.position) if controlled and ball.position else 1.0
        # 当前不启用通用“非蓝色区域=对手”启发式；它会把草地纹理和界面元素误报成大量对手。
        opponents: list[PlayerObservation] = []
        opponent_ball_distance = min((distance(player.position, ball.position) for player in opponents), default=1.0) if ball.position else 1.0
        nearest_opponent = min(opponents, key=lambda player: distance(player.position, controlled), default=None) if controlled else None
        nearest_opponent_distance = distance(nearest_opponent.position, controlled) if nearest_opponent and controlled else 1.0
        possession = Possession.UNKNOWN
        if controlled and ball.position and ball_distance <= 0.12:
            possession = Possession.OUR_TEAM
        elif ball.position and opponent_ball_distance <= 0.12:
            possession = Possession.OPPONENT
        elif ball.position:
            possession = Possession.LOOSE
        pressure = max(0.0, min(1.0, 1.0 - nearest_opponent_distance / 0.45))
        opponent_has_ball = possession == Possession.OPPONENT
        danger = max(0.0, min(1.0, (0.60 * (1.0 - opponent_ball_distance / 0.45) if opponent_has_ball else 0.0) + 0.25 * (1.0 - nearest_opponent_distance / 0.45) + 0.15 * (1.0 if ball.position and ball.position[0] < 0.35 else 0.0)))
        passes = []
        if controlled:
            for teammate in teammates:
                if distance(teammate.position, controlled) < 0.04:
                    continue
                pass_distance = distance(controlled, teammate.position)
                passes.append(PassingOpportunity(teammate.position, max(0.0, 1.0 - pass_distance), pass_distance, max(0.0, 1.0 - pressure), pressure, False, "PASS"))
        shooting = max(0.0, min(1.0, (controlled[0] - 0.50) / 0.50)) if controlled and ball.position else 0.0
        dribble_space = max(0.0, min(1.0, 1.0 - pressure)) if controlled else 0.0
        phase = Phase.ATTACK if possession == Possession.OUR_TEAM else Phase.DEFENSE if possession == Possession.OPPONENT else Phase.TRANSITION
        confidence = min(1.0, 0.25 * controlled_confidence + 0.25 * (ball.confidence if ball.position else 0.0) + 0.20 * (sum(player.confidence for player in teammates) / max(1, len(teammates))) + 0.15 * (1.0 if opponents else 0.0) + 0.15)
        state = GameState(
            timestamp=time.time(),
            game_detected=True,
            possession=possession,
            phase=phase,
            controlled_player_position=controlled,
            ball_position=ball.position,
            field_zone=field_zone(controlled) if controlled else "UNKNOWN",
            visible_teammates=teammates,
            visible_opponents=opponents,
            nearest_opponent_position=nearest_opponent.position if nearest_opponent else None,
            nearest_opponent_distance=nearest_opponent_distance,
            ball_distance_to_controlled_player=ball_distance,
            pressure_level=pressure,
            shooting_opportunity=shooting,
            passing_opportunities=passes,
            dribble_space=dribble_space,
            danger_level=danger,
            confidence=confidence if controlled and ball.position else min(0.30, confidence),
            controlled_player_changed=changed,
            receiving=changed and ball_distance < 0.14,
            metadata={"vision_note": "marker_ball_opponents", "marker_confidence": marker_confidence, "ball_confidence": ball.confidence, "opponent_count": len(opponents), "ball_in_own_half": bool(ball.position and ball.position[0] < 0.5), "opponent_has_ball": opponent_has_ball},
        )
        return frame, state

    @staticmethod
    def _find_opponents(frame) -> list[PlayerObservation]:
        """粗略寻找非蓝色球衣；具体效果仍需按实际画面调参。"""
        try:
            import cv2
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, np.array((0, 70, 45)), np.array((179, 255, 255)))
            mask[((hsv[:, :, 0] >= 35) & (hsv[:, :, 0] <= 95)) | ((hsv[:, :, 0] >= 90) & (hsv[:, :, 0] <= 140))] = 0
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            height, width = frame.shape[:2]
            output = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 18 or area > width * height * 0.01:
                    continue
                moments = cv2.moments(contour)
                if moments["m00"]:
                    output.append(PlayerObservation((moments["m10"] / moments["m00"] / width, moments["m01"] / moments["m00"] / height), min(1.0, area / 120.0)))
            return output
        except Exception:
            return []

    @staticmethod
    def _unknown() -> GameState:
        return GameState(timestamp=time.time(), game_detected=False, confidence=0.0)

    def close(self) -> None:
        self.capture.close()
