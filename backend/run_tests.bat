@echo off
REM Run ggNet Backend Tests (Windows)
REM Usage:
REM   run_tests.bat              - Run all tests
REM   run_tests.bat storage      - Run storage tests only
REM   run_tests.bat -v           - Verbose output

echo ========================================
echo   ggNet Backend Tests
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
pip install --upgrade pip >nul 2>&1

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt >nul 2>&1

REM Run tests
echo Running tests...
echo.

if "%1"=="storage" (
    pytest tests\test_storage_manager.py -v
) else if "%1"=="-v" (
    pytest -v
) else (
    pytest
)

echo.
echo ========================================
echo   Tests completed!
echo ========================================

pause

