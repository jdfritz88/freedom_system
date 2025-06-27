@echo off
cd /d F:\Apps\freedom_system

REM Stop tracking oversized files without deleting them locally

git rm --cached componentsave/envs/coqui_env/Lib/site-packages/sudachidict_core/resources/system.dic

git rm --cached componentsave/envs/coqui_env/Lib/site-packages/torch/lib/torch_cpu.dll

git rm --cached componentsave/envs/coqui_env/Lib/site-packages/torch/lib/dnnl.lib

REM Commit the removal and push

git commit -m "Remove oversized files from tracking to comply with GitHub limits"
git push
