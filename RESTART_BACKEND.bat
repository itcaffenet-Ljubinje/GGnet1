@echo off
echo ========================================
echo   Stopping ggNet Backend...
echo ========================================
echo.

taskkill /F /IM python.exe /FI "WINDOWTITLE eq ggNet Backend*" 2>nul

timeout /t 2 /nobreak > nul

echo ========================================
echo   Starting ggNet Backend...
echo ========================================
echo.

start "ggNet Backend" cmd /k "cd backend && set PYTHONPATH=src && venv\Scripts\python.exe src\main.py"

echo.
echo Backend restarted!
echo.
pause

