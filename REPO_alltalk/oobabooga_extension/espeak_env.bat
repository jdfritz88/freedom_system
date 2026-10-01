@echo off
rem eSpeak NG (the phonemes tool) lives in app_cabinet\espeak-ng, not installed system-wide.
rem Called by the oobabooga launcher (REPO_boredom\launch_oobabooga.bat) so eSpeak is on PATH
rem for oobabooga and the AllTalk server its AllTalk add-on starts. No setlocal: the settings
rem must stay set in the launcher that calls this file.
set "FREEDOM_ESPEAK=F:\Apps\freedom_system\app_cabinet\espeak-ng\eSpeak NG"
set "PATH=%FREEDOM_ESPEAK%;%PATH%"
set "PHONEMIZER_ESPEAK_LIBRARY=%FREEDOM_ESPEAK%\libespeak-ng.dll"
set "PHONEMIZER_ESPEAK_PATH=%FREEDOM_ESPEAK%\espeak-ng.exe"
set "ESPEAK_DATA_PATH=%FREEDOM_ESPEAK%\espeak-ng-data"
