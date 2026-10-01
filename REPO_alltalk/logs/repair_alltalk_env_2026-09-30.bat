@echo off
rem Repair of AllTalk's environment after AllTalk's F5-TTS engine ran its own
rem `pip install git+https://github.com/SWivid/F5-TTS.git` on 2026-09-30, which replaced
rem 66 packages (PyTorch 2.2.1+cu121 -> 2.14.1+cpu, Gradio 4.44.1 -> 6.29, FastAPI,
rem Transformers 5.18, ...) and stopped AllTalk starting for every engine.
rem
rem 1. PyTorch goes back exactly as conda's own records list it (conda-meta), the way
rem    AllTalk's atsetup.bat installed it; --no-deps so nothing else conda manages moves.
rem 2. pip puts AllTalk's pinned requirements back, with F5-TTS 1.1.7 (the newest release
rem    whose requirements accept Gradio 4.44.1) and Transformers below 5 (5.1+ needs
rem    PyTorch 2.4+). Same set the dry run of 2026-09-30 resolved: 14 packages change.
rem
rem Only AllTalk's own environment is used, by full path - never a global Python
rem (user rule 2026-09-30: each component has its own Python and PyTorch).
setlocal
set "ENV=F:\Apps\freedom_system\app_cabinet\alltalk_tts\alltalk_environment"
set "PY=%ENV%\env\python.exe"
set "CONDA=%ENV%\conda\condabin\conda.bat"
set "APP=F:\Apps\freedom_system\app_cabinet\alltalk_tts"
set "CONSTRAINTS=%~dp0repair_alltalk_constraints_2026-09-30.txt"
cd /D "%APP%" || exit /b 1
call "%CONDA%" activate "%ENV%\env" || exit /b 1

echo ===== 1/3 remove pip's PyTorch 2.14.1+cpu and torchaudio 2.11.0 =====
"%PY%" -m pip uninstall -y torch torchaudio || exit /b 2

echo ===== 2/3 conda: PyTorch 2.2.1 CUDA 12.1 builds from conda-meta =====
call "%CONDA%" install -p "%ENV%\env" -y --force-reinstall --no-deps "pytorch==2.2.1=py3.11_cuda12.1_cudnn8_0" "torchaudio==2.2.1=py311_cu121" "torchvision==0.17.1=py311_cu121" -c pytorch -c nvidia || exit /b 3
"%PY%" -c "import torch; print('torch', torch.__version__, 'cuda', torch.version.cuda, 'available', torch.cuda.is_available())" || exit /b 4

echo ===== 3/3 pip: AllTalk requirements + Gradio 4.44.1 + F5-TTS 1.1.7, locked =====
"%PY%" -m pip install -r system\requirements\requirements_standalone.txt gradio==4.44.1 f5-tts==1.1.7 -c "%CONSTRAINTS%" || exit /b 5
"%PY%" -m pip check
"%PY%" -c "import torch, transformers, gradio, fastapi, f5_tts; print('torch', torch.__version__, torch.version.cuda, torch.cuda.is_available(), '| transformers', transformers.__version__, '| gradio', gradio.__version__, '| fastapi', fastapi.__version__)" || exit /b 6
echo ===== repair finished =====
