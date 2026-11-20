@echo off
echo ========================================================
echo Launching CampusTrack AI Full Stack Platform...
echo ========================================================

start "CampusTrack AI - Flask Backend" cmd /k "py -3.12 -m backend.app"
start "CampusTrack AI - React Frontend" cmd /k "cd frontend && npm run dev"

echo Backend running on http://127.0.0.1:5000
echo Frontend running on http://localhost:5173
echo.

