@echo off
rem REPO_alltalk launcher: starts stock AllTalk (app_cabinet\alltalk_tts) and tells it
rem to use REPO_alltalk for your changes, settings, voices, outputs and logs - the way
rem ComfyUI is started with --base-directory. AllTalk's own folder is never changed.
rem
rem Graphics card (CUDA) or main processor (CPU) mode - added 2026-09-30.
rem Main processor mode hides the graphics card from AllTalk, so it uses none of its
rem memory (DeepSpeed is switched off for that run by patches\alltalk_patches.py).
rem Switching modes restarts AllTalk. Files every app can read:
rem   settings\device_mode.txt   the saved mode: cuda or cpu (missing = cuda). Any app
rem                              switches modes by writing it; the launcher that is running
rem                              AllTalk sees the change and restarts it in the new mode.
rem   runtime\running_mode.txt   the mode the running AllTalk was started in
rem   runtime\alltalk.pid        the running AllTalk's process id (its script.py)
rem   runtime\request.txt        another app writes "restart" or "stop" here
rem
rem   launch_alltalk.bat                 5-second mode menu, then AllTalk with a key menu
rem   launch_alltalk.bat --choose-mode   only the 5-second mode menu: saves the pick, exits
rem   FREEDOM_ALLTALK_HEADLESS=1         set by a caller whose window takes no keys (the
rem                                      KoboldCpp launcher runs AllTalk in the background):
rem                                      no countdown and no key menu; switches still work
setlocal EnableExtensions
set "FREEDOM_ALLTALK_REPO=%~dp0"
if "%FREEDOM_ALLTALK_REPO:~-1%"=="\" set "FREEDOM_ALLTALK_REPO=%FREEDOM_ALLTALK_REPO:~0,-1%"
if not defined FREEDOM_ALLTALK_APP set "FREEDOM_ALLTALK_APP=F:\Apps\freedom_system\app_cabinet\alltalk_tts"
if not defined FREEDOM_ALLTALK_ENV set "FREEDOM_ALLTALK_ENV=F:\Apps\freedom_system\app_cabinet\alltalk_tts\alltalk_environment"
set "PYTHONPATH=%FREEDOM_ALLTALK_REPO%\_boot"

set "MODE_FILE=%FREEDOM_ALLTALK_REPO%\settings\device_mode.txt"
set "RUNTIME=%FREEDOM_ALLTALK_REPO%\runtime"
set "PID_FILE=%RUNTIME%\alltalk.pid"
set "RUNNING_FILE=%RUNTIME%\running_mode.txt"
set "REQUEST_FILE=%RUNTIME%\request.txt"
set "ALLTALK_PORT=7851"
set "ORIG_CUDA_VISIBLE_DEVICES=%CUDA_VISIBLE_DEVICES%"

set "CHOOSE_ONLY="
set "PASS_ARGS="
:args
if "%~1"=="" goto args_done
if /I "%~1"=="--choose-mode" (set "CHOOSE_ONLY=1") else set PASS_ARGS=%PASS_ARGS% %1
shift
goto args
:args_done

if defined CHOOSE_ONLY (
    call :choose_mode
    exit /b 0
)
call :choose_mode

rem eSpeak NG (the phonemes tool) lives in app_cabinet\espeak-ng, not installed system-wide;
rem it is put on PATH only for the programs this launcher starts.
set "FREEDOM_ESPEAK=F:\Apps\freedom_system\app_cabinet\espeak-ng\eSpeak NG"
set "PATH=%FREEDOM_ESPEAK%;%PATH%"
set "PHONEMIZER_ESPEAK_LIBRARY=%FREEDOM_ESPEAK%\libespeak-ng.dll"
set "PHONEMIZER_ESPEAK_PATH=%FREEDOM_ESPEAK%\espeak-ng.exe"
set "ESPEAK_DATA_PATH=%FREEDOM_ESPEAK%\espeak-ng-data"

rem Weekly update check (asks before installing; reports go to REPO_alltalk\logs\update_checks.log)
powershell -NoProfile -ExecutionPolicy Bypass -File "%FREEDOM_ALLTALK_REPO%\update_check.ps1" -App "%FREEDOM_ALLTALK_APP%"

cd /D "%FREEDOM_ALLTALK_APP%" || exit /b 1
call "%FREEDOM_ALLTALK_ENV%\conda\condabin\conda.bat" activate "%FREEDOM_ALLTALK_ENV%\env" || exit /b 1
if not exist "%RUNTIME%" mkdir "%RUNTIME%"

call :port_in_use
if not errorlevel 1 (
    echo.
    echo   AllTalk is already running ^(port %ALLTALK_PORT% is in use^) - not starting a second copy.
    echo   Switch its mode from the window that started it, or from any app's AllTalk mode option.
    exit /b 1
)

rem ------------------------------------------------------------------ run AllTalk
:run
call :read_saved_mode
set "RUN_MODE=%SAVED_MODE%"
call :mode_label %RUN_MODE%
if /I "%RUN_MODE%"=="cpu" (set "CUDA_VISIBLE_DEVICES=-1") else (set "CUDA_VISIBLE_DEVICES=%ORIG_CUDA_VISIBLE_DEVICES%")
if exist "%REQUEST_FILE%" del "%REQUEST_FILE%" >nul 2>&1
echo.
echo   Starting AllTalk on the %LABEL% ...
>"%RUNNING_FILE%" echo %RUN_MODE%
start "" /b python script.py%PASS_ARGS%
call :find_pid
if not defined AT_PID (
    echo   AllTalk did not start - see the messages above.
    call :clear_runtime
    exit /b 1
)
>"%PID_FILE%" echo %AT_PID%
set "READY="

rem ------------------------------------------------------------------ watch loop
rem Every ~2 seconds: take a menu key (if this window takes keys), check AllTalk is
rem still running, and act on a request or a mode switch made by another app.
:watch
set "K=6"
if defined FREEDOM_ALLTALK_HEADLESS goto watch_sleep
choice /c CPRQMX /n /t 2 /d X >nul
set "K=%errorlevel%"
if "%K%"=="255" goto watch_sleep
goto watch_check
:watch_sleep
ping -n 3 127.0.0.1 >nul
:watch_check
tasklist /fi "PID eq %AT_PID%" /nh 2>nul | find " %AT_PID% " >nul || goto ended
if not defined READY call :check_ready
if "%K%"=="1" (set "WANT=cuda" & goto switch)
if "%K%"=="2" (set "WANT=cpu" & goto switch)
if "%K%"=="3" (set "WHY=R was pressed" & goto restart)
if "%K%"=="4" goto stop
if "%K%"=="5" call :show_menu
set "REQ="
if exist "%REQUEST_FILE%" for /f "usebackq tokens=1" %%r in ("%REQUEST_FILE%") do set "REQ=%%r"
if exist "%REQUEST_FILE%" del "%REQUEST_FILE%" >nul 2>&1
if /I "%REQ%"=="restart" (set "WHY=another app asked for a restart" & goto restart)
if /I "%REQ%"=="stop" goto stop
call :read_saved_mode
if /I not "%SAVED_MODE%"=="%RUN_MODE%" (set "WHY=another app switched the mode" & goto restart)
goto watch

:switch
if /I "%WANT%"=="%RUN_MODE%" (
    call :mode_label %RUN_MODE%
    call :echo_label_line "  Already running on the "
    goto watch
)
>"%MODE_FILE%" echo %WANT%
set "WHY=mode switched"
:restart
echo.
echo   Restarting AllTalk ^(%WHY%^) ...
call :kill_alltalk
if errorlevel 1 goto port_stuck
goto run

:stop
echo.
echo   Stopping AllTalk ...
call :kill_alltalk
if errorlevel 1 (
    call :clear_runtime
    echo   Port %ALLTALK_PORT% is STILL held - AllTalk did not fully stop. Check Task Manager.
    exit /b 1
)
call :clear_runtime
echo   AllTalk stopped.
exit /b 0

:ended
echo.
echo   AllTalk has closed.
call :clear_runtime
exit /b 0

:port_stuck
echo   Port %ALLTALK_PORT% is still held after stopping AllTalk - not starting a second copy.
call :clear_runtime
exit /b 1

rem ------------------------------------------------------------------ subroutines
:choose_mode
rem The 5-second startup menu. No key = the saved mode. A picked mode is saved.
call :read_saved_mode
if defined FREEDOM_ALLTALK_HEADLESS exit /b 0
call :mode_label %SAVED_MODE%
echo.
echo  ======================= AllTalk mode =======================
echo    Saved mode: %LABEL%
echo      C = graphics card ^(CUDA^)
echo      P = main processor ^(CPU^) - leaves the graphics card free
echo      S = start now with the saved mode
echo    No key within 5 seconds = start with the saved mode.
echo  =============================================================
set /a LEFT=5
:cd_tick
<nul set /p "=   %LEFT%... "
choice /c CPSX /n /t 1 /d X >nul
set "K=%errorlevel%"
if "%K%"=="1" (set "PICK=cuda" & goto cd_picked)
if "%K%"=="2" (set "PICK=cpu" & goto cd_picked)
if "%K%"=="3" goto cd_saved
if "%K%"=="255" goto cd_saved
set /a LEFT-=1
if %LEFT% GTR 0 goto cd_tick
:cd_saved
echo.
call :echo_label_line "   Using the saved mode: "
exit /b 0
:cd_picked
>"%MODE_FILE%" echo %PICK%
set "SAVED_MODE=%PICK%"
call :mode_label %PICK%
echo.
call :echo_label_line "   Picked and saved: "
exit /b 0

:read_saved_mode
set "SAVED_MODE=cuda"
if exist "%MODE_FILE%" for /f "usebackq tokens=1" %%m in ("%MODE_FILE%") do set "SAVED_MODE=%%m"
if /I not "%SAVED_MODE%"=="cpu" set "SAVED_MODE=cuda"
exit /b 0

:mode_label
if /I "%~1"=="cpu" (set "LABEL=main processor (CPU)") else (set "LABEL=graphics card (CUDA)")
exit /b 0

:echo_label_line
echo %~1%LABEL%
exit /b 0

:show_menu
call :mode_label %RUN_MODE%
rem (LABEL has brackets in it, so it is never echoed inside a bracketed block)
if not defined FREEDOM_ALLTALK_HEADLESS goto sm_keys
echo   AllTalk is running on the %LABEL%.
exit /b 0
:sm_keys
echo.
echo  =================== AllTalk mode menu ===================
echo    Running on the %LABEL%
echo      C = switch to graphics card ^(CUDA^)
echo      P = switch to main processor ^(CPU^)
echo      R = restart AllTalk     Q = stop AllTalk
echo      M = show this menu again
echo    Switching restarts AllTalk; speech pauses until it is back.
echo  =========================================================
exit /b 0

:check_ready
call :port_in_use
if errorlevel 1 exit /b 0
set "READY=1"
call :show_menu
exit /b 0

:port_in_use
rem errorlevel 0 = something is listening on the AllTalk port
netstat -ano -p tcp | findstr /r /c:":%ALLTALK_PORT% .*LISTENING" >nul
exit /b %errorlevel%

:find_pid
rem The AllTalk just started: this environment's python running script.py.
set "AT_PID="
set /a TRIES=0
:fp_try
set /a TRIES+=1
ping -n 2 127.0.0.1 >nul
for /f "usebackq delims=" %%p in (`powershell -NoProfile -Command "$e = $env:FREEDOM_ALLTALK_ENV + '\env\python.exe'; Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.ExecutablePath -eq $e -and $_.CommandLine -match 'script\.py' } | Select-Object -First 1 -ExpandProperty ProcessId"`) do set "AT_PID=%%p"
if defined AT_PID exit /b 0
if %TRIES% LSS 15 goto fp_try
exit /b 1

:kill_alltalk
taskkill /T /F /PID %AT_PID% >nul 2>&1
set /a WAITED=0
:ka_wait
call :port_in_use
if errorlevel 1 exit /b 0
rem When AllTalk switches engine it restarts its server as a NEW process (os.execv), which
rem is outside the process tree stopped above. Stop whichever AllTalk python holds the port
rem (only AllTalk's own environment's python - never anything else on that port).
if %WAITED% GEQ 2 call :kill_port_owner
set /a WAITED+=1
if %WAITED% GEQ 30 exit /b 1
ping -n 2 127.0.0.1 >nul
goto ka_wait

:kill_port_owner
for /f "tokens=5" %%p in ('netstat -ano -p tcp ^| findstr /r /c:":%ALLTALK_PORT% .*LISTENING"') do (
    powershell -NoProfile -Command "$p = Get-Process -Id %%p -ErrorAction SilentlyContinue; if ($p -and $p.Path -like '*\alltalk_environment\*') { exit 0 } else { exit 1 }" && taskkill /T /F /PID %%p >nul 2>&1
)
exit /b 0

:clear_runtime
if exist "%PID_FILE%" del "%PID_FILE%" >nul 2>&1
if exist "%RUNNING_FILE%" del "%RUNNING_FILE%" >nul 2>&1
if exist "%REQUEST_FILE%" del "%REQUEST_FILE%" >nul 2>&1
exit /b 0
