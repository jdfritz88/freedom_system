@echo off
rem REPO_oobabooga launcher: starts stock oobabooga (app_cabinet\text-generation-webui)
rem with its user folder (settings, characters, extensions, models, logs) in
rem REPO_oobabooga\user_data - oobabooga's own --user-data-dir setting, the way ComfyUI
rem is started with --base-directory. Oobabooga's own folder is never changed.
setlocal
set "REPO_OOBABOOGA=%~dp0"
if "%REPO_OOBABOOGA:~-1%"=="\" set "REPO_OOBABOOGA=%REPO_OOBABOOGA:~0,-1%"
if not defined OOBABOOGA_APP set "OOBABOOGA_APP=F:\Apps\freedom_system\app_cabinet\text-generation-webui"

call "%OOBABOOGA_APP%\start_windows.bat" --user-data-dir "%REPO_OOBABOOGA%\user_data" %*
