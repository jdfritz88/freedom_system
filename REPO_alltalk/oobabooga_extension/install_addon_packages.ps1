# Installs the AllTalk add-on's own packages (addon_requirements.txt) into oobabooga's
# conda environment. Oobabooga does not ship them, so REPO_boredom\update_check.ps1 runs this
# after every oobabooga update. Returns @{ code = <pip exit code>; out = <last lines of output> }.
param(
    [string]$App = "F:\Apps\freedom_system\app_cabinet\text-generation-webui"
)
$req = Join-Path $PSScriptRoot "addon_requirements.txt"
$conda = Join-Path $App "installer_files\conda\condabin\conda.bat"
$envdir = Join-Path $App "installer_files\env"
$out = cmd /c "cd /D `"$App`" && call `"$conda`" activate `"$envdir`" && python -m pip install -r `"$req`"" 2>&1
return @{ code = $LASTEXITCODE; out = ($out | Select-Object -Last 8) -join "`r`n" }
