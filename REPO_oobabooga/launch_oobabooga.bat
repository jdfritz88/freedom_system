@echo off
rem REPO_oobabooga launcher: starts stock oobabooga (app_cabinet\text-generation-webui)
rem with its user folder (settings, characters, extensions, models, logs) in
rem REPO_oobabooga\user_data - oobabooga's own --user-data-dir setting, the way ComfyUI
rem is started with --base-directory. Oobabooga's own folder is never changed.
setlocal
set "REPO_OOBABOOGA=%~dp0"
if "%REPO_OOBABOOGA:~-1%"=="\" set "REPO_OOBABOOGA=%REPO_OOBABOOGA:~0,-1%"
if not defined OOBABOOGA_APP set "OOBABOOGA_APP=F:\Apps\freedom_system\app_cabinet\text-generation-webui"

rem eSpeak NG (the phonemes tool) lives in app_cabinet\espeak-ng, not installed system-wide;
rem on PATH only for oobabooga and the AllTalk server its add-on starts.
set "FREEDOM_ESPEAK=F:\Apps\freedom_system\app_cabinet\espeak-ng\eSpeak NG"
set "PATH=%FREEDOM_ESPEAK%;%PATH%"
set "PHONEMIZER_ESPEAK_LIBRARY=%FREEDOM_ESPEAK%\libespeak-ng.dll"
set "PHONEMIZER_ESPEAK_PATH=%FREEDOM_ESPEAK%\espeak-ng.exe"
set "ESPEAK_DATA_PATH=%FREEDOM_ESPEAK%\espeak-ng-data"

call "%OOBABOOGA_APP%\start_windows.bat" --user-data-dir "%REPO_OOBABOOGA%\user_data" %*
