@echo off
REM ============================================================================
REM Text Injection Test Runner
REM ============================================================================
REM Runs the comprehensive injection test app with all 14 verification methods
REM Tests 26 injection methods including CHARACTER_GREETING (proven pattern)
REM ============================================================================

setlocal

REM Set paths
set PYTHON_EXE=F:\Apps\freedom_system\freedom_system_2000\text-generation-webui\installer_files\env\python.exe
set TEST_APP_DIR=F:\Apps\freedom_system\injection_test_app
set TEST_SCRIPT=%TEST_APP_DIR%\run_all_tests.py

REM Check if Python exists
if not exist "%PYTHON_EXE%" (
    echo ERROR: Python not found at %PYTHON_EXE%
    pause
    exit /b 1
)

REM Check if test script exists
if not exist "%TEST_SCRIPT%" (
    echo ERROR: Test script not found at %TEST_SCRIPT%
    pause
    exit /b 1
)

echo ============================================================================
echo                    TEXT INJECTION TEST RUNNER
echo ============================================================================
echo.
echo Test App: %TEST_APP_DIR%
echo Python:   %PYTHON_EXE%
echo.
echo Options:
echo   --quick    : Run quick tests (most reliable methods)
echo   --full     : Run full tests (all methods x all 14 verifications)
echo   --selenium : Include Selenium browser verification
echo.
echo ============================================================================

REM Change to test app directory
cd /d "%TEST_APP_DIR%"

REM Run the test with any arguments passed to this batch file
"%PYTHON_EXE%" "%TEST_SCRIPT%" %*

echo.
echo ============================================================================
echo Test complete. Check logs in F:\Apps\freedom_system\log\
echo ============================================================================
pause
