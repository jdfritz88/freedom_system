@echo off
echo ========================================
echo  Freedom Whisper STT Server
echo  Port: 8787
echo ========================================
cd /d "%~dp0"
call venv\Scripts\activate.bat
python server.py
pause
