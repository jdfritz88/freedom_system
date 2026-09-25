@echo off
REM ============================================================
REM Chat Inject Monitor - Startup Script
REM ============================================================
REM This batch file starts the Chat Inject Monitor GUI application
REM using the text-generation-webui Python environment.
REM ============================================================

echo ============================================================
echo Chat Inject Monitor - Starting...
echo ============================================================
echo.

REM Set the Python executable path from the text-generation-webui environment
set PYTHON_EXE=F:\Apps\freedom_system\freedom_system_2000\text-generation-webui\installer_files\env\python.exe

REM Set the script path
set SCRIPT_PATH=%~dp0chat_inject_monitor.py

REM Check if Python exists
if not exist "%PYTHON_EXE%" (
    echo ERROR: Python executable not found at:
    echo %PYTHON_EXE%
    echo.
    echo Please check that text-generation-webui is installed correctly.
    pause
    exit /b 1
)

REM Check if script exists
if not exist "%SCRIPT_PATH%" (
    echo ERROR: chat_inject_monitor.py not found at:
    echo %SCRIPT_PATH%
    echo.
    pause
    exit /b 1
)

echo Python: %PYTHON_EXE%
echo Script: %SCRIPT_PATH%
echo.
echo Starting GUI application...
echo.

REM Start the application
"%PYTHON_EXE%" "%SCRIPT_PATH%"

REM If we get here, the application closed
echo.
echo Chat Inject Monitor has closed.
pause
