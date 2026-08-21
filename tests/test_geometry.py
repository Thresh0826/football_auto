from efootball_agent.vision.geometry import danger_zone, distance, field_zone, normalize_point


def test_normalize_point():
    assert normalize_point((50, 25), 100, 50) == (0.5, 0.5)


def test_distance_and_zone():
    assert round(distance((0, 0), (0.3, 0.4)), 5) == 0.5
    assert field_zone((0.9, 0.5)) == "PENALTY_AREA"
    assert danger_zone((0.1, 0.5))

