# REPO_alltalk weekly update check - run by launch_alltalk.bat before AllTalk starts.
# Checks AllTalk's GitHub branch (the developer's v2 code, branch alltalkbeta) at most once
# every 7 days. If new code exists it shows what changed and asks Yes/No; it installs only on
# Yes. Every check with something to report is written to REPO_alltalk\logs\update_checks.log.
param(
    [string]$App = "F:\Apps\freedom_system\app_cabinet\alltalk_tts",
    [string]$Repo = $PSScriptRoot,
    [switch]$Force,                      # ignore the 7-day gate
    [ValidateSet("", "Yes", "No")]
    [string]$Answer = ""                 # answer without a dialog (scripted runs)
)
# "Continue": git writes normal progress to stderr, which "Stop" would treat as a failure.
# Every git/pip step is checked through $LASTEXITCODE instead.
$ErrorActionPreference = "Continue"
$Branch = "alltalkbeta"
$Logs = Join-Path $Repo "logs"
$StateFile = Join-Path $Logs "update_check_state.json"
$LogFile = Join-Path $Logs "update_checks.log"
New-Item -ItemType Directory -Force $Logs | Out-Null

function Write-Report([string]$text) {
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LogFile -Encoding UTF8 -Value "===== $stamp AllTalk update check =====`r`n$text`r`n"
}
function Save-State { @{ last_check = (Get-Date).ToString("o") } | ConvertTo-Json | Set-Content -Encoding UTF8 $StateFile }
function Ask([string]$title, [string]$text) {
    if ($Answer) { return $Answer }
    Add-Type -AssemblyName System.Windows.Forms
    $r = [System.Windows.Forms.MessageBox]::Show($text, $title, "YesNo", "Question")
    return $r.ToString()
}

if (-not $Force -and (Test-Path $StateFile)) {
    $last = [datetime](Get-Content $StateFile -Raw | ConvertFrom-Json).last_check
    if (((Get-Date) - $last).TotalDays -lt 7) { exit 0 }
}

$fetch = git -C $App fetch --quiet origin $Branch 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Report "Could not reach AllTalk's GitHub to check for updates (git fetch exit $LASTEXITCODE): $($fetch -join ' ')`r`nAllTalk starts as it is; the check runs again next launch."
    exit 0   # no state saved: try again next launch
}
Save-State

$count = [int](git -C $App rev-list --count "HEAD..origin/$Branch")
if ($count -eq 0) { exit 0 }

$commits = (git -C $App log --oneline --max-count 15 "HEAD..origin/$Branch") -join "`r`n"
$changed = @(git -C $App diff --name-only "HEAD" "origin/$Branch")
# Stock files the REPO_alltalk patches change (keys of PATCHES in patches\alltalk_patches.py)
$patched = @(Select-String -Path (Join-Path $Repo "patches\alltalk_patches.py") -Pattern '^\s{4}"([^"]+\.py)":\s*\[' |
             ForEach-Object { $_.Matches[0].Groups[1].Value })
$touched = @($changed | Where-Object { $patched -contains $_ })
$reqChanged = @($changed | Where-Object { $_ -like "system/requirements/*" })

$msg = "AllTalk has $count new update(s) from the developer (branch $Branch):`r`n`r`n$commits"
if ($touched.Count) {
    $msg += "`r`n`r`nThese updated files are ones your REPO_alltalk patches change:`r`n  " + ($touched -join "`r`n  ") +
            "`r`nIf the developer rewrote the patched lines, AllTalk will refuse to start and name the patch until it is updated."
}
if ($reqChanged.Count) { $msg += "`r`n`r`nAllTalk's package requirements changed too; they will be reinstalled." }
$msg += "`r`n`r`nInstall the update now?"

$reply = Ask "AllTalk update available" $msg
$report = "$count update(s) available.`r`n$commits`r`nFiles your patches change that were updated: " +
          ($(if ($touched.Count) { $touched -join ", " } else { "none" })) + "`r`nYour answer: $reply"

if ($reply -ne "Yes") { Write-Report "$report`r`nNot installed."; exit 0 }

# Tell the app-folder watcher a developer update is being installed (not alerted).
$WindowFile = Join-Path $Logs "watcher_update_window.json"
$windowStart = (Get-Date).ToString("s")
@{ start = $windowStart; end = $null } | ConvertTo-Json | Set-Content -Encoding UTF8 $WindowFile
$before = git -C $App rev-parse --short HEAD
$pull = git -C $App pull --ff-only origin $Branch 2>&1
if ($LASTEXITCODE -ne 0) {
    @{ start = $windowStart; end = (Get-Date).ToString("s") } | ConvertTo-Json | Set-Content -Encoding UTF8 $WindowFile
    Write-Report "$report`r`nUPDATE FAILED - git pull: $($pull -join ' ')`r`nAllTalk left at $before."
    exit 0
}
$after = git -C $App rev-parse --short HEAD
$report += "`r`nUpdated AllTalk $before -> $after."

if ($reqChanged.Count) {
    $env_dir = Join-Path $App "alltalk_environment"
    $req = Join-Path $App "system\requirements\requirements_standalone.txt"
    $pip = cmd /c "call `"$env_dir\conda\condabin\conda.bat`" activate `"$env_dir\env`" && python -m pip install -r `"$req`"" 2>&1
    $report += "`r`nRequirements reinstalled from requirements_standalone.txt (exit $LASTEXITCODE):`r`n" + (($pip | Select-Object -Last 5) -join "`r`n")
}
@{ start = $windowStart; end = (Get-Date).ToString("s") } | ConvertTo-Json | Set-Content -Encoding UTF8 $WindowFile
Write-Report $report
