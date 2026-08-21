from __future__ import annotations

import time
from dataclasses import dataclass

from efootball_agent.action.action import Action, ActionKind
from efootball_agent.config import DecisionConfig
from efootball_agent.state.enums import AgentState, Phase, Possession
from efootball_agent.state.game_state import GameState
from .cooldown import Cooldown
from .scoring import best_pass, score_defensive_press, score_dribble, score_pass, score_shoot, score_tackle


@dataclass
class Decision:
    state: AgentState
    action: Action
    pass_score: float = 0.0
    shoot_score: float = 0.0
    dribble_score: float = 0.0


class Brain:
    def __init__(self, config: DecisionConfig | None = None) -> None:
        self.config = config or DecisionConfig()
        self.state = AgentState.IDLE
        self.cooldown = Cooldown()
        self._candidate = self.state
        self._candidate_count = 0
        self._last_transition = 0.0

    def _target_state(self, game: GameState) -> AgentState:
        if not game.game_detected or game.confidence < 0.22:
            return AgentState.IDLE
        if game.receiving or game.controlled_player_changed:
            return AgentState.RECEIVING
        if game.possession == Possession.OUR_TEAM:
            return AgentState.POSSESSION
        if game.possession == Possession.OPPONENT:
            return AgentState.DEFEND_DANGER if game.danger_level >= self.config.danger_threshold else AgentState.DEFEND_NORMAL
        if game.phase == Phase.ATTACK:
            return AgentState.ATTACK_OFF_BALL
        if game.phase == Phase.DEFENSE:
            return AgentState.DEFEND_NORMAL
        return AgentState.TRANSITION_DEFENSE if game.phase == Phase.TRANSITION else AgentState.IDLE

    def _stabilize(self, target: AgentState, now: float) -> None:
        if target == self.state:
            self._candidate = target
            self._candidate_count = 0
            return
        if target != self._candidate:
            self._candidate = target
            self._candidate_count = 1
            return
        self._candidate_count += 1
        if self._candidate_count >= self.config.state_confirm_frames and now - self._last_transition >= self.config.state_cooldown:
            self.state = target
            self._last_transition = now
            self._candidate_count = 0

    def decide(self, game: GameState) -> Decision:
        now = time.monotonic()
        self._stabilize(self._target_state(game), now)
        if self.state == AgentState.IDLE or game.confidence < 0.35:
            return Decision(self.state, Action(ActionKind.RELEASE_ALL, reason="low_vision_confidence"))
        # 门将持球不参与短传/盘带，固定执行解围；我方半场高压时也优先解围。
        if game.metadata.get("goalkeeper_has_ball"):
            return Decision(self.state, Action(ActionKind.CLEAR, duration=0.12, reason="goalkeeper_clear_only"))
        if game.metadata.get("clearance_required") or (game.metadata.get("ball_in_own_half") and game.pressure_level >= 0.86):
            return Decision(self.state, Action(ActionKind.CLEAR, duration=0.12, reason="emergency_clearance"))
        if self.state in (AgentState.DEFEND_DANGER, AgentState.DEFEND_NORMAL, AgentState.TRANSITION_DEFENSE):
            return self._defend(game)
        if self.state == AgentState.RECEIVING:
            return Decision(self.state, Action(ActionKind.MOVE, direction=game.goal_direction, intensity=0.35, duration=0.15, reason="receive_and_scan"))
        if self.state == AgentState.ATTACK_OFF_BALL:
            return Decision(self.state, Action(ActionKind.MOVE, direction=game.goal_direction, intensity=0.28, duration=0.20, reason="support_position"))
        return self._attack(game)

    def _defend(self, game: GameState) -> Decision:
        press = score_defensive_press(game)
        tackle = score_tackle(game)
        passing = score_pass(game)
        shooting = score_shoot(game)
        dribbling = score_dribble(game)
        if game.confidence < 0.50:
            return Decision(self.state, Action(ActionKind.MOVE, direction=game.goal_direction, intensity=0.22, duration=0.18, reason="conservative_defense"), passing, shooting, dribbling)
        direction = game.metadata.get("defensive_direction", game.goal_direction)
        if self.state == AgentState.DEFEND_DANGER and tackle >= 0.72 and self.cooldown.ready("tackle"):
            self.cooldown.trigger("tackle", 0.65, time.monotonic())
            return Decision(self.state, Action(ActionKind.TACKLE, duration=0.10, reason="danger_close_ball"), passing, shooting, dribbling)
        if self.state == AgentState.DEFEND_DANGER or press >= 0.60:
            return Decision(self.state, Action(ActionKind.PRESS, direction=direction, intensity=0.65, duration=0.25, reason="close_shot_lane"), passing, shooting, dribbling)
        return Decision(self.state, Action(ActionKind.MOVE, direction=direction, intensity=0.38, duration=0.25, reason="cover_and_contain"), passing, shooting, dribbling)

    def _attack(self, game: GameState) -> Decision:
        passing = score_pass(game)
        shooting = score_shoot(game)
        dribbling = score_dribble(game)
        if shooting >= self.config.shoot_threshold and self.cooldown.ready("shoot"):
            self.cooldown.trigger("shoot", 0.55)
            return Decision(self.state, Action(ActionKind.SHOOT, direction=game.goal_direction, power=0.72, duration=0.10, reason="clear_shooting_chance"), passing, shooting, dribbling)
        target = best_pass(game)
        if target and passing >= self.config.pass_threshold and game.pressure_level >= 0.48 and self.cooldown.ready("pass"):
            self.cooldown.trigger("pass", 0.35)
            direction = (target.target[0] - (game.controlled_player_position or (0.5, 0.5))[0], target.target[1] - (game.controlled_player_position or (0.5, 0.5))[1])
            kind = {"LOB_PASS": ActionKind.LOB_PASS, "THROUGH_PASS": ActionKind.THROUGH_PASS, "FLY_THROUGH": ActionKind.FLY_THROUGH}.get(target.pass_type, ActionKind.PASS)
            return Decision(self.state, Action(kind, direction=direction, power=0.58, duration=0.08, reason="safe_pass_under_pressure"), passing, shooting, dribbling)
        if dribbling >= self.config.dribble_threshold:
            return Decision(self.state, Action(ActionKind.SPRINT, direction=game.goal_direction, intensity=0.62, duration=0.35, reason="open_space_progression"), passing, shooting, dribbling)
        if target and passing >= self.config.pass_threshold and self.cooldown.ready("pass"):
            self.cooldown.trigger("pass", 0.35)
            kind = {"LOB_PASS": ActionKind.LOB_PASS, "THROUGH_PASS": ActionKind.THROUGH_PASS, "FLY_THROUGH": ActionKind.FLY_THROUGH}.get(target.pass_type, ActionKind.PASS)
            return Decision(self.state, Action(kind, direction=(target.target[0] - 0.5, target.target[1] - 0.5), power=0.50, duration=0.08, reason="forward_safe_pass"), passing, shooting, dribbling)
        return Decision(self.state, Action(ActionKind.MOVE, direction=game.goal_direction, intensity=0.30, duration=0.20, reason="hold_and_reassess"), passing, shooting, dribbling)
