from efootball_agent.state.enums import Possession


def infer_possession(ball_distance: float, opponent_distance: float, threshold: float = 0.08) -> Possession:
    if ball_distance <= threshold and ball_distance < opponent_distance:
        return Possession.OUR_TEAM
    if opponent_distance <= threshold and opponent_distance < ball_distance:
        return Possession.OPPONENT
    if min(ball_distance, opponent_distance) < 0.20:
        return Possession.LOOSE
    return Possession.UNKNOWN

