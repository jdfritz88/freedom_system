@echo off
echo ========================================
echo  VS Code + Claude Code + Voice Mod
echo  AllTalk TTS  :  port 7851
echo  Whisper STT  :  port 8787
echo ========================================
echo.

REM --- Start AllTalk TTS ---
echo [1/4] Starting AllTalk TTS on port 7851...
start "AllTalk TTS" cmd /k "cd /d F:\Apps\freedom_system\freedom_system_2000\alltalk_tts && call start_alltalk.bat"

REM --- Start Whisper STT ---
echo [2/4] Starting Whisper STT on port 8787...
start "Whisper STT" cmd /k "cd /d F:\Apps\freedom_system\freedom_system_2000\whisper_stt && call venv\Scripts\activate.bat && python server.py"

REM --- Start Microphone Control Panel ---
echo [3/4] Starting Microphone Control Panel...
start "Mic Panel" cmd /k "cd /d F:\Apps\freedom_system\REPO_vs_claude_code_voice_mode && call venv\Scripts\activate.bat && python mic_panel.py"

REM --- Wait for services ---
echo.
echo Waiting for services to be ready...
:wait_loop
timeout /t 3 /nobreak >nul 2>&1

REM Check AllTalk
curl -s http://127.0.0.1:7851/api/ready >nul 2>&1
if errorlevel 1 (
    echo   Waiting for AllTalk TTS...
    goto wait_loop
)

REM Check Whisper
curl -s http://127.0.0.1:8787/health >nul 2>&1
if errorlevel 1 (
    echo   Waiting for Whisper STT...
    goto wait_loop
)

echo.
echo ========================================
echo  All services ready!
echo  AllTalk TTS:  http://127.0.0.1:7851
echo  Whisper STT:  http://127.0.0.1:8787
echo  Mic Panel:    Running
echo ========================================
echo.

REM --- Start VS Code with Claude Code ---
echo [4/4] Starting VS Code with Claude Code...
"F:\Apps\VSCode\bin\code.cmd" "F:\Apps\freedom_system"

echo.
echo ========================================
echo  VS Code + Claude Code + Voice Mod
echo  is running. Close this window to shut
echo  down all voice services.
echo ========================================
echo.
echo Press any key to shut down all services...
pause >nul

echo.
echo Shutting down services...
taskkill /fi "WINDOWTITLE eq AllTalk TTS" /t /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq Whisper STT" /t /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq Mic Panel" /t /f >nul 2>&1
echo Done.
