from __future__ import annotations

from pathlib import Path
import math

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def run_calibration(config_path: str, calibration_path: str) -> int:
    print("校准模式：请先启动 scrcpy，并让比赛画面和经典虚拟按键完整可见。")
    if yaml is None:
        print("缺少 PyYAML，无法保存校准文件。")
        return 2
    try:
        import cv2
        from efootball_agent.capture.dxcam_capture import DxcamCapture
    except Exception as exc:
        print(f"需要 DXcam 和 OpenCV 才能进行点击校准：{exc}")
        return 2
    try:
        source = DxcamCapture(None, 15)
    except Exception as exc:
        print(f"DXcam 初始化失败：{exc}")
        print("请确认使用 64 位 Python，并更新显卡驱动后重试。")
        return 2
    frame = source.read()
    if frame is None:
        source.close()
        print("没有读到桌面画面，请确认 scrcpy 已启动并允许屏幕采集。")
        return 2
    result: dict[str, object] = {}
    attack_steps = [
        ("screen_tl", "点击 scrcpy 比赛画面左上角"),
        ("screen_br", "点击 scrcpy 比赛画面右下角"),
        ("joystick_center", "点击左侧虚拟摇杆中心"),
        ("joystick_edge", "点击摇杆边缘任意一点"),
        ("pass_button", "点击进攻状态的传球按钮中心"),
        ("pass_swipe_end", "点击从传球按钮向上滑动的终点"),
        ("through_button", "点击进攻状态的直塞球按钮中心"),
        ("through_swipe_end", "点击从直塞按钮向上滑动的终点"),
        ("shoot_button", "点击进攻状态的射门按钮"),
        ("sprint_button", "点击冲刺按钮"),
        ("control_marker_center", "点击当前控制球员头顶的控制标记中心"),
    ]
    points: dict[str, tuple[int, int]] = {}
    def collect(frame_to_show, steps):
        index = 0

        def on_mouse(event, x, y, _flags, _param):
            nonlocal index
            if event == cv2.EVENT_LBUTTONDOWN and index < len(steps):
                points[steps[index][0]] = (int(x), int(y))
                index += 1

        window = "eFootball Agent Calibration"
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window, frame_to_show.shape[1], frame_to_show.shape[0])
        cv2.moveWindow(window, 0, 0)
        cv2.setMouseCallback(window, on_mouse)
        while index < len(steps):
            current = frame_to_show.copy()
            text = f"{index + 1}/{len(steps)}: {steps[index][1]} | R=重来 Q=退出"
            cv2.rectangle(current, (0, 0), (current.shape[1], 62), (0, 0, 0), -1)
            cv2.putText(current, text, (20, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.82, (255, 255, 255), 2, cv2.LINE_AA)
            for point in points.values():
                cv2.circle(current, point, 12, (0, 0, 0), 5)
                cv2.circle(current, point, 9, (0, 255, 0), 3)
            cv2.imshow(window, current)
            key = cv2.waitKey(30) & 0xFF
            if key in (ord("q"), 27):
                cv2.destroyWindow(window)
                return False
            if key == ord("r"):
                points.clear()
                index = 0
        cv2.destroyWindow(window)
        return True

    if not collect(frame, attack_steps):
        source.close()
        return 1
    marker_frame = frame.copy()
    input("请现在在手机上切换到防守状态，然后回到此窗口按回车继续：")
    frame = source.read()
    if frame is None:
        source.close()
        print("切换到防守画面后没有读到桌面画面。")
        return 2
    if not collect(frame, [("pressure_button", "点击防守状态的施压按钮"), ("tackle_button", "点击防守状态的铲球/抢断按钮")]):
        source.close()
        return 1
    cv2.destroyAllWindows()
    input("请让手机进入我方半场持球/门将持球状态，然后回到此窗口按回车继续：")
    frame = source.read()
    if frame is None:
        print("切换到解围画面后没有读到桌面画面。")
        source.close()
        return 2
    if not collect(frame, [("clear_button", "点击解围按钮")]):
        source.close()
        return 1
    source.close()
    source.close()
    tl, br = points["screen_tl"], points["screen_br"]
    center, edge = points["joystick_center"], points["joystick_edge"]
    result["screen_region"] = {"left": min(tl[0], br[0]), "top": min(tl[1], br[1]), "right": max(tl[0], br[0]), "bottom": max(tl[1], br[1])}
    result["joystick_center"] = {"x": center[0], "y": center[1]}
    result["joystick_radius"] = round(math.hypot(edge[0] - center[0], edge[1] - center[1]), 1)
    for key in ("pass_button", "pass_swipe_end", "through_button", "through_swipe_end", "shoot_button", "sprint_button", "pressure_button", "tackle_button", "clear_button"):
        point = points[key]
        result[key] = {"x": point[0], "y": point[1]}
    marker = points["control_marker_center"]
    template_dir = Path("config/templates")
    template_dir.mkdir(parents=True, exist_ok=True)
    x, y = marker
    crop = marker_frame[max(0, y - 20):y + 21, max(0, x - 30):x + 31]
    template_path = template_dir / "control_marker.png"
    cv2.imwrite(str(template_path), crop)
    result["control_marker_template"] = str(template_path).replace("\\", "/")
    path = Path(calibration_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(result, handle, allow_unicode=True, sort_keys=False)
    print(f"已保存：{path}")
    return 0
