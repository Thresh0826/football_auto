# eFootball Agent V1

这是一个面向 Android 手机《实况足球》经典虚拟按键模式的外部视觉 Agent。它只读取屏幕画面，并通过 scrcpy 镜像窗口进行普通鼠标按住、拖动和释放，不读取游戏内存、不注入 DLL、不修改网络协议。

## 当前版本

已包含：

- GameState、攻防状态机、连续帧确认、滞后和 cooldown。
- 基于规则评分的传球、射门、推进、普通防守和危险防守。
- Dry Run、Replay、录制日志、OpenCV Debug Overlay。
- Android/scrcpy 接入所需的 DXcam 桌面采集接口。
- 经典模式虚拟摇杆的持续按住、方向移动和释放。
- 高空传球、直塞、高空直塞和解围动作校准及动作映射；高空传球/高空直塞使用基础按钮按住后滑动。
- 门将持球固定解围、我方半场高压紧急解围规则。
- 蓝色我方球衣的 OpenCV HSV 检测基础接口。
- MockVisionProvider 和 pytest 模拟场景。

## 安装

Windows 10/11、Python 3.12：

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Android 手机连接电脑时，安装官方 scrcpy，打开 USB 调试并允许电脑调试。先启动 scrcpy，使手机比赛画面显示在 Windows 窗口中。

## 运行

先运行模拟场景：

```bat
python app.py --self-test
```

开发测试，不发送触控：

```bat
python app.py --dry-run
```

校准：

```bat
python app.py --calibrate
```

校准程序会截取当前桌面并显示点击提示。按顺序点击比赛区域、摇杆、传球按钮及其向上滑动终点、直塞按钮及其向上滑动终点、射门和冲刺；切换防守状态后点击施压和抢断，再切换到我方半场持球或门将持球状态点击解围。坐标会保存为 Windows 桌面坐标。

正式运行前必须确认 calibration.yaml 正确，然后：

```bat
python app.py
```

按 ESC 关闭 Debug Overlay，按 Ctrl+C 停止。程序异常退出时会执行 release_all，避免摇杆或按钮保持按下。

## 配置

`config/default.yaml` 控制 FPS、蓝色 HSV 范围、危险阈值、评分阈值、状态确认帧数和动作 cooldown。

`config/calibration.yaml` 保存手机镜像窗口中的摇杆与按钮坐标。对方球衣不固定，因此不使用固定对方颜色。

## 测试

```bat
pytest -q
```

## 录像和日志

日志在 `logs/agent.log`。将 `debug.recording` 设为 `true` 后，决策记录写入 `recordings/`，可用：

```bat
python app.py --replay recordings/recording-xxxx.jsonl
```

## 当前限制

真实手机画面尚未连接，因此视觉检测和触控坐标仍需用你的实际 scrcpy 画面校准。没有画面、足球或控制标记证据时，系统会降级并释放输入，不会在未知画面上随机操作。经典模式的移动摇杆与按钮可能需要多点触控；scrcpy 官方支持控制和虚拟第二指，但实际按钮布局必须用你的手机画面验证。若手机厂商要求，需额外打开“USB 调试（安全设置）”。
