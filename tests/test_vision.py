import numpy as np

from efootball_agent.vision.ball_detector import BallDetector
from efootball_agent.vision.player_detector import PlayerDetector
from efootball_agent.vision.tracker import NearestNeighborTracker


def test_tracker_keeps_nearby_points():
    tracker = NearestNeighborTracker(max_distance=0.1)
    tracker.update([(0.2, 0.2)])
    assert tracker.update([(0.21, 0.2), (0.8, 0.8)]) == [(0.21, 0.2)]


def test_detectors_are_safe_on_empty_frame():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    assert PlayerDetector().detect_our_team(frame) == []
    assert BallDetector().detect(frame, 1.0).position is None

