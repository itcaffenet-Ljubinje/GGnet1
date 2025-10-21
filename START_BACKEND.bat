@echo off
echo ========================================
echo   ggNet Backend Startup
echo ========================================
echo.

cd backend
set PYTHONPATH=src
venv\Scripts\python.exe src\main.py

pause

