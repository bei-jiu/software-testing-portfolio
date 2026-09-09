@echo off
chcp 65001 >nul
setlocal

REM =====================================================
REM   PDD App Automation Test - One-click Launcher
REM   Double-click to run all cases.
REM   Run a single case:  run.bat -k collect
REM =====================================================

cd /d "%~dp0"

set "ADB=C:\android-sdk\platform-tools\adb.exe"
set "DEVICE=emulator-5554"

echo.
echo  ==========================================
echo    PDD App Automation Test Launcher
echo  ==========================================
echo.

echo  [1/3] Checking emulator...
"%ADB%" devices | findstr "%DEVICE%" >nul
if errorlevel 1 (
    echo.
    echo  [X] Emulator %DEVICE% not found.
    echo      Please start MuMu emulator first,
    echo      and make sure PDD is installed and logged in.
    echo.
    pause
    exit /b 1
)
echo       [OK] Emulator connected
echo.

echo  [2/3] Checking Appium...
curl -s -m 3 http://127.0.0.1:4723/status | findstr "ready" >nul
if errorlevel 1 (
    echo       Appium not running, starting it now...
    start "Appium Server" appium
    timeout /t 8 /nobreak >nul
    curl -s -m 3 http://127.0.0.1:4723/status | findstr "ready" >nul
    if errorlevel 1 (
        echo.
        echo  [X] Appium failed to start. Start Appium manually and retry.
        echo.
        pause
        exit /b 1
    )
)
echo       [OK] Appium is ready
echo.

echo  [3/3] Running tests...
echo  --------------------------------------------------
echo.
python -m pytest -v -s %*
echo.
echo  --------------------------------------------------
echo.
echo  Done. PASSED = passed, FAILED = failed.
echo  Screenshots are saved in the screenshots folder.
echo.
echo  ==========================================
pause
endlocal
