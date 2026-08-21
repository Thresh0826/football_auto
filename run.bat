@echo off
set PY=%~dp0.venv\Scripts\python.exe
if not exist "%PY%" set PY=python
"%PY%" app.py --dry-run
pause
