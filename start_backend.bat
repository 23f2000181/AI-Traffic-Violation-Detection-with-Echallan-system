@echo off
echo Starting Traffic Violation Detection Backend Server...
echo.
cd /d "%~dp0"
python backend\app.py
pause
