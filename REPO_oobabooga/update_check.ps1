# REPO_oobabooga weekly update check - run by launch_oobabooga.bat before oobabooga starts.
# Checks oobabooga's GitHub for a newer stable release (v* tags) at most once every 7 days.
# If one exists it asks Yes/No and installs only on Yes. Every check with something to report
# is written to REPO_oobabooga\logs\update_checks.log.
param(
    [string]$App = "F:\Apps\freedom_system\app_cabinet\text-generation-webui",
    [string]$Repo = $PSScriptRoot,
    [string]$BackupRoot = "F:\Apps",     # old environments are moved here, never deleted
    [switch]$Force,                      # ignore the 7-day gate
    [ValidateSet("", "Yes", "No")]
    [string]$Answer = ""                 # answer without a dialog (scripted runs)
)
# "Continue": git writes normal progress to stderr, which "Stop" would treat as a failure.
# Every git/pip step is checked through $LASTEXITCODE instead.
$ErrorActionPreference = "Continue"
$Logs = Join-Path $Repo "logs"
$StateFile = Join-Path $Logs "update_check_state.json"
$LogFile = Join-Path $Logs "update_checks.log"
New-Item -ItemType Directory -Force $Logs | Out-Null

function Write-Report([string]$text) {
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LogFile -Encoding UTF8 -Value "===== $stamp oobabooga update check =====`r`n$text`r`n"
}
function Save-State { @{ last_check = (Get-Date).ToString("o") } | ConvertTo-Json | Set-Content -Encoding UTF8 $StateFile }
function Ask([string]$title, [string]$text) {
    if ($Answer) { return $Answer }
    Add-Type -AssemblyName System.Windows.Forms
    return [System.Windows.Forms.MessageBox]::Show($text, $title, "YesNo", "Question").ToString()
}
function In-Env([string]$command) {
    # Run a command inside oobabooga's own conda environment.
    $conda = Join-Path $App "installer_files\conda\condabin\conda.bat"
    $envdir = Join-Path $App "installer_files\env"
    $out = cmd /c "cd /D `"$App`" && call `"$conda`" activate `"$envdir`" && $command" 2>&1
    return @{ code = $LASTEXITCODE; out = ($out | Select-Object -Last 8) -join "`r`n" }
}

if (-not $Force -and (Test-Path $StateFile)) {
    $last = [datetime](Get-Content $StateFile -Raw | ConvertFrom-Json).last_check
    if (((Get-Date) - $last).TotalDays -lt 7) { exit 0 }
}

$fetch = git -C $App fetch --quiet --tags origin 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Report "Could not reach oobabooga's GitHub to check for updates (git fetch exit $LASTEXITCODE): $($fetch -join ' ')`r`noobabooga starts as it is; the check runs again next launch."
    exit 0   # no state saved: try again next launch
}
Save-State

$current = (git -C $App describe --tags --exact-match HEAD 2>$null)
if (-not $current) { $current = "(no release tag) " + (git -C $App rev-parse --short HEAD) }
$latest = (git -C $App tag -l "v*" --sort=-v:refname | Select-Object -First 1)
if (-not $latest -or $latest -eq $current) { exit 0 }
git -C $App merge-base --is-ancestor HEAD $latest
$ahead = ($LASTEXITCODE -eq 0) -and ((git -C $App rev-parse HEAD) -ne (git -C $App rev-parse "$latest^{commit}"))
if (-not $ahead) { exit 0 }

$envPy = Join-Path $App "installer_files\env\python.exe"
$pyNow = $(if (Test-Path $envPy) { & $envPy -c "import sys;print('%d.%d'%sys.version_info[:2])" } else { "" })
$pyNew = ((git -C $App show "${latest}:one_click.py") | Select-String -Pattern '^PYTHON_VERSION = "([0-9.]+)"' | ForEach-Object { $_.Matches[0].Groups[1].Value })
# A fresh environment is needed when none exists or the release needs a different Python.
$freshEnv = (-not $pyNow) -or ($pyNew -and ($pyNow -ne $pyNew))

$msg = "A new oobabooga release is available: $latest (you have $current).`r`n`r`n" +
       "Release notes: https://github.com/oobabooga/textgen/releases/tag/$latest"
if ($freshEnv) {
    $msg += "`r`n`r`nThis release needs Python $pyNew (installed: $(if ($pyNow) { $pyNow } else { 'none' })), so oobabooga's environment will be rebuilt " +
            "(several GB download). The old one is moved to a backup folder, not deleted."
}
$msg += "`r`n`r`nInstall it now?"
$reply = Ask "oobabooga update available" $msg
$report = "Release $latest available (installed: $current). Python: now $pyNow, new $pyNew.`r`nYour answer: $reply"
if ($reply -ne "Yes") { Write-Report "$report`r`nNot installed."; exit 0 }

$co = git -C $App -c advice.detachedHead=false checkout $latest 2>&1
if ($LASTEXITCODE -ne 0) { Write-Report "$report`r`nUPDATE FAILED - git checkout: $($co -join ' ')`r`noobabooga left at $current."; exit 0 }
$report += "`r`nCode updated $current -> $latest."

if ($freshEnv) {
    $backup = Join-Path $BackupRoot ("freedom_system_BACKUP_ooba_" + ($current -replace '[^\w.-]', '_'))
    New-Item -ItemType Directory -Force $backup | Out-Null
    if (Test-Path (Join-Path $App "installer_files")) {
        Move-Item -LiteralPath (Join-Path $App "installer_files") -Destination (Join-Path $backup "installer_files")
        $report += "`r`nOld environment moved to $backup\installer_files."
    }
    # Build the new environment with the developer's own installer, without starting the UI.
    $env:GPU_CHOICE = "A"; $env:LAUNCH_AFTER_INSTALL = "no"
    $build = cmd /c "echo.| `"$App\start_windows.bat`"" 2>&1
    Remove-Item Env:\LAUNCH_AFTER_INSTALL
    $report += "`r`nNew environment built (exit $LASTEXITCODE):`r`n" + (($build | Select-Object -Last 6) -join "`r`n")
} else {
    $r = In-Env "python -c `"import one_click; one_click.update_requirements(pull=False)`""
    $report += "`r`nRequirements updated for $latest (exit $($r.code)):`r`n$($r.out)"
}

# The AllTalk add-on's own packages (oobabooga does not ship them).
$r = In-Env "python -m pip install -r `"$Repo\addon_requirements.txt`""
$report += "`r`nAdd-on packages (addon_requirements.txt) installed (exit $($r.code)):`r`n$($r.out)"
Write-Report $report
