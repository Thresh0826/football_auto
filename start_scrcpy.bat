@echo off
set SCRCPY=D:\scrcpy\scrcpy-win64-v4.1\scrcpy.exe
if not exist "%SCRCPY%" (
    echo 找不到 scrcpy：%SCRCPY%
    pause
    exit /b 1
)
"%SCRCPY%" --window-title="eFootball scrcpy" --max-size=1600 --max-fps=60 --stay-awake
