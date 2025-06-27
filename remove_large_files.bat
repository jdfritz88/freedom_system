@echo off
REM Git Large File Fix (.bat version)
REM Removes oversized files and purges Git history

cd /d F:\Apps\freedom_system

REM Step 1: Untrack large files
git rm --cached componentsave/envs/coqui_env/Lib/site-packages/sudachidict_core/resources/system.dic
git rm --cached componentsave/envs/coqui_env/Lib/site-packages/torch/lib/torch_cpu.dll
git rm --cached componentsave/envs/coqui_env/Lib/site-packages/torch/lib/dnnl.lib

REM Step 2: Add to .gitignore
echo componentsave/envs/coqui_env/Lib/site-packages/sudachidict_core/resources/system.dic>>.gitignore
echo componentsave/envs/coqui_env/Lib/site-packages/torch/lib/torch_cpu.dll>>.gitignore
echo componentsave/envs/coqui_env/Lib/site-packages/torch/lib/dnnl.lib>>.gitignore

REM Step 3: Rewrite history (requires git-filter-repo)
git filter-repo --path componentsave/envs/coqui_env/Lib/site-packages/sudachidict_core/resources/system.dic --invert-paths
git filter-repo --path componentsave/envs/coqui_env/Lib/site-packages/torch/lib/torch_cpu.dll --invert-paths
git filter-repo --path componentsave/envs/coqui_env/Lib/site-packages/torch/lib/dnnl.lib --invert-paths

REM Step 4: Re-add remote (if necessary)
git remote add origin https://github.com/jdfritz88/freedom_system.git

REM Step 5: Force push to GitHub
git push -f origin main

pause
