from __future__ import annotations

import argparse
import time
from pathlib import Path

from efootball_agent.config import load_config
from efootball_agent.decision.brain import Brain
from efootball_agent.input_layer.dry_run import DryRunInputBackend
from efootball_agent.input_layer.win32_input import Win32InputBackend
from efootball_agent.action.planner import ActionPlanner
from efootball_agent.vision.mock_provider import MockVisionProvider
from efootball_agent.vision.live_provider import LiveVisionProvider
from efootball_agent.debug.overlay import Overlay
from efootball_agent.debug.recorder import Recorder
from efootball_agent.debug.replay import replay_file
from efootball_agent.calibration.calibrator import run_calibration
from efootball_agent.utils.logger import get_logger


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Android eFootball external vision agent")
    parser.add_argument("--config", default="config/default.yaml")
    parser.add_argument("--calibration", default="config/calibration.yaml")
    parser.add_argument("--dry-run", action="store_true", help="决策正常运行，但不发送触控")
    parser.add_argument("--calibrate", action="store_true")
    parser.add_argument("--replay", type=Path)
    parser.add_argument("--self-test", action="store_true")
    return parser


def run_self_test() -> int:
    provider = MockVisionProvider()
    for name in ("dribble", "pass", "shoot", "defense", "danger", "receiving"):
        brain = Brain()
        planner = ActionPlanner(DryRunInputBackend(), {})
        state = provider.case(name)
        decision = brain.decide(state)
        for _ in range(2):
            decision = brain.decide(state)
        planner.execute(decision.action)
        print(f"{name:10s} state={decision.state.value:20s} action={decision.action.kind.value}")
    return 0


def run_live(args: argparse.Namespace) -> int:
    logger = get_logger()
    config = load_config(args.config, args.calibration)
    backend = DryRunInputBackend() if args.dry_run else Win32InputBackend(config.capture.scrcpy_title)
    planner = ActionPlanner(backend, config.calibration)
    brain = Brain(config.decision)
    overlay = Overlay(config.debug)
    recorder = Recorder(config.debug.recording_dir) if config.debug.recording else None
    try:
        provider = LiveVisionProvider.create(config.capture, config.vision, config.calibration)
    except Exception as exc:
        logger.error("无法启动真实画面采集：%s；进入安全停止模式", exc)
        provider = None
    period = 1.0 / max(1.0, config.decision.tick_rate)
    logger.info("agent started dry_run=%s; 按 ESC 或 Ctrl+C 停止", args.dry_run)
    try:
        while True:
            started = time.perf_counter()
            if provider is None:
                frame, state = None, MockVisionProvider().case("unknown")
                state.game_detected = False
                state.confidence = 0.0
            else:
                frame, state = provider.next()
            decision = brain.decide(state)
            planner.execute(decision.action)
            if recorder:
                recorder.write(frame, state, decision)
            if overlay.enabled:
                if overlay.show(frame, state, decision) == 27:
                    break
            elapsed = time.perf_counter() - started
            time.sleep(max(0.0, period - elapsed))
    except KeyboardInterrupt:
        logger.info("stopped by keyboard interrupt")
    finally:
        planner.release_all()
        if recorder:
            recorder.close()
        overlay.close()
        if provider is not None:
            provider.close()
    return 0


def main() -> int:
    args = build_parser().parse_args()
    if args.self_test:
        return run_self_test()
    if args.calibrate:
        return run_calibration(args.config, args.calibration)
    if args.replay:
        return replay_file(args.replay, args.config)
    return run_live(args)


if __name__ == "__main__":
    raise SystemExit(main())
