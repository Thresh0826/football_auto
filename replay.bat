@echo off
set /p FILE=Recording file: 
set PY=%~dp0.venv\Scripts\python.exe
if not exist "%PY%" set PY=python
"%PY%" app.py --replay "%FILE%"
pause
