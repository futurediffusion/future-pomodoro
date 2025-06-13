@echo off
REM Actualiza el repositorio y ejecuta la aplicacion Pomodoro
cd /d "%~dp0"
git pull
python pomodoro.py
