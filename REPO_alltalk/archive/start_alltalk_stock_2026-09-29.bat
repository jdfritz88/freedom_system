@echo off 
cd /D "F:\Apps\freedom_system\app_cabinet\alltalk_tts\" 
set CONDA_ROOT_PREFIX=F:\Apps\freedom_system\app_cabinet\alltalk_tts\alltalk_environment\conda 
set INSTALL_ENV_DIR=F:\Apps\freedom_system\app_cabinet\alltalk_tts\alltalk_environment\env 
call "F:\Apps\freedom_system\app_cabinet\alltalk_tts\alltalk_environment\conda\condabin\conda.bat" activate "F:\Apps\freedom_system\app_cabinet\alltalk_tts\alltalk_environment\env" 
call python script.py 
