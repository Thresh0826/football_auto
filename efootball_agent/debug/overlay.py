from __future__ import annotations

from typing import Any

from efootball_agent.state.game_state import GameState
from efootball_agent.decision.brain import Decision


class Overlay:
    def __init__(self, config: Any) -> None:
        self.enabled = bool(getattr(config, "overlay", True))
        self.show_frame = bool(getattr(config, "show_frame", False))
        self._cv2 = None

    def show(self, frame, state: GameState, decision: Decision) -> int:
        if not self.enabled or frame is None:
            return -1
        try:
            import cv2
            self._cv2 = cv2
            state_names = {"IDLE": "空闲", "ATTACK_OFF_BALL": "进攻无球", "RECEIVING": "接球", "POSSESSION": "我方控球", "DEFEND_NORMAL": "正常防守", "DEFEND_DANGER": "危险防守", "TRANSITION_ATTACK": "攻防转换-进攻", "TRANSITION_DEFENSE": "攻防转换-防守"}
            action_names = {"RELEASE_ALL": "释放全部按键", "MOVE": "移动", "SPRINT": "冲刺", "PASS": "地面传球", "LOB_PASS": "高空传球", "THROUGH_PASS": "直塞球", "FLY_THROUGH": "高空直塞", "SHOOT": "射门", "TACKLE": "铲球", "PRESS": "施压", "CLEAR": "解围"}
            possession_names = {"OUR_TEAM": "我方", "OPPONENT": "对方", "LOOSE": "无人控制", "UNKNOWN": "未知"}
            reason_names = {"cover_and_contain": "回防占位", "conservative_defense": "保守防守", "close_shot_lane": "封堵射门路线", "danger_close_ball": "危险区域抢断", "hold_and_reassess": "观察后再决策", "receive_and_scan": "接球观察", "safe_pass_under_pressure": "受压安全传球", "forward_safe_pass": "向前安全传球", "emergency_clearance": "紧急解围", "goalkeeper_clear_only": "门将持球固定解围"}
            metadata = state.metadata or {}
            lines = [f"状态：{state_names.get(decision.state.value, decision.state.value)}    识别度：{state.confidence:.2f}", f"球权：{possession_names.get(state.possession.value, state.possession.value)}    危险：{state.danger_level:.2f}    压力：{state.pressure_level:.2f}", f"传球评分：{decision.pass_score:.2f}    带球评分：{decision.dribble_score:.2f}    射门评分：{decision.shoot_score:.2f}", f"球置信度：{metadata.get('ball_confidence', 0.0):.2f}    控球距离：{state.ball_distance_to_controlled_player:.2f}", f"标记置信度：{metadata.get('marker_confidence', 0.0):.2f}    对手数量：{metadata.get('opponent_count', len(state.visible_opponents))}", f"动作：{action_names.get(decision.action.kind.value, decision.action.kind.value)}    原因：{reason_names.get(decision.action.reason, decision.action.reason)}"]
            if self.show_frame and frame is not None:
                image = frame.copy()
                height, width = image.shape[:2]
                panel_width = min(width, 900)
                panel_height = min(height, 145)
                cv2.rectangle(image, (0, 0), (panel_width, panel_height), (0, 0, 0), -1)
            else:
                # 不把采集到的桌面画回调试窗口，避免 DXCam 再次捕获本窗口造成递归叠加。
                image = __import__("numpy").zeros((225, 1180, 3), dtype="uint8")
            for index, line in enumerate(lines):
                cv2.putText(image, line, (15, 30 + index * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow("eFootball Agent Debug", image)
            return cv2.waitKey(1) & 0xFF
        except ImportError:
            return -1

    def close(self) -> None:
        if self._cv2 is not None:
            self._cv2.destroyAllWindows()
