from __future__ import annotations

import json
import time
from pathlib import Path


class Recorder:
    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / f"recording-{int(time.time())}.jsonl"
        self.handle = self.path.open("w", encoding="utf-8")
        self.video_path = self.path.with_suffix(".mp4")
        self.writer = None

    def write(self, frame, state, decision) -> None:
        if frame is not None:
            try:
                import cv2
                if self.writer is None:
                    height, width = frame.shape[:2]
                    self.writer = cv2.VideoWriter(str(self.video_path), cv2.VideoWriter_fourcc(*"mp4v"), 30.0, (width, height))
                self.writer.write(frame)
            except Exception:
                self.writer = None
        record = {"timestamp": state.timestamp, "state": {"phase": state.phase.value, "possession": state.possession.value, "confidence": state.confidence, "danger": state.danger_level}, "decision": {"state": decision.state.value, "action": decision.action.kind.value, "reason": decision.action.reason}}
        self.handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.handle.flush()

    def close(self) -> None:
        if self.writer is not None:
            self.writer.release()
        self.handle.close()
