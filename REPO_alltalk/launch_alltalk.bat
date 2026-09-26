@echo off
rem REPO_alltalk launcher: starts stock AllTalk (app_cabinet\alltalk_tts) and tells it
rem to use REPO_alltalk for your changes, settings, voices, outputs and logs - the way
rem ComfyUI is started with --base-directory. AllTalk's own folder is never changed.
setlocal
set "FREEDOM_ALLTALK_REPO=%~dp0"
if "%FREEDOM_ALLTALK_REPO:~-1%"=="\" set "FREEDOM_ALLTALK_REPO=%FREEDOM_ALLTALK_REPO:~0,-1%"
if not defined FREEDOM_ALLTALK_APP set "FREEDOM_ALLTALK_APP=F:\Apps\freedom_system\app_cabinet\alltalk_tts"
if not defined FREEDOM_ALLTALK_ENV set "FREEDOM_ALLTALK_ENV=F:\Apps\freedom_system\app_cabinet\alltalk_tts\alltalk_environment"
set "PYTHONPATH=%FREEDOM_ALLTALK_REPO%\_boot"

rem eSpeak NG (the phonemes tool) lives in app_cabinet\espeak-ng, not installed system-wide;
rem it is put on PATH only for the programs this launcher starts.
set "FREEDOM_ESPEAK=F:\Apps\freedom_system\app_cabinet\espeak-ng\eSpeak NG"
set "PATH=%FREEDOM_ESPEAK%;%PATH%"
set "PHONEMIZER_ESPEAK_LIBRARY=%FREEDOM_ESPEAK%\libespeak-ng.dll"
set "PHONEMIZER_ESPEAK_PATH=%FREEDOM_ESPEAK%\espeak-ng.exe"
set "ESPEAK_DATA_PATH=%FREEDOM_ESPEAK%\espeak-ng-data"

cd /D "%FREEDOM_ALLTALK_APP%" || exit /b 1
call "%FREEDOM_ALLTALK_ENV%\conda\condabin\conda.bat" activate "%FREEDOM_ALLTALK_ENV%\env" || exit /b 1
python script.py %*
