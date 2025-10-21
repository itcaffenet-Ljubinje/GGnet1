@echo off
echo ========================================
echo   ggNet Services Startup Script
echo ========================================
echo.

echo [1/2] Starting Backend...
start "ggNet Backend" cmd /k "cd backend && set PYTHONPATH=src && venv\Scripts\python.exe src\main.py"
timeout /t 3 /nobreak > nul

echo [2/2] Starting Frontend...
start "ggNet Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo   Services Started!
echo ========================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Press any key to exit...
pause > nul

