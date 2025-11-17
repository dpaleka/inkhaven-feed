@echo off
setlocal enabledelayedexpansion
REM Inkhaven Feed Viewer - Startup Script
REM Starts both the feed monitor and display viewer

echo ==========================================
echo Starting Inkhaven Feed Viewer
echo ==========================================
echo.

REM Check if PID files exist and processes are still running
if exist .monitor.pid (
    set /p MONITOR_PID=<.monitor.pid
    tasklist /FI "PID eq !MONITOR_PID!" 2>NUL | find "!MONITOR_PID!" >NUL
    if not errorlevel 1 (
        echo WARNING: Feed monitor is already running ^(PID: !MONITOR_PID!^)
        echo    Run kill.bat first to stop existing processes
        exit /b 1
    )
    del .monitor.pid
)

if exist .viewer.pid (
    set /p VIEWER_PID=<.viewer.pid
    tasklist /FI "PID eq !VIEWER_PID!" 2>NUL | find "!VIEWER_PID!" >NUL
    if not errorlevel 1 (
        echo WARNING: Display viewer is already running ^(PID: !VIEWER_PID!^)
        echo    Run kill.bat first to stop existing processes
        exit /b 1
    )
    del .viewer.pid
)

REM Start feed monitor in background
echo Starting feed monitor...
start "InkhavenFeedMonitor" /B cmd /c "uv run -m feed_monitor > feed_monitor.log 2>&1"
timeout /t 1 /nobreak >NUL

REM Get PID of feed monitor
for /f "tokens=2" %%a in ('wmic process where "commandline like '%%feed_monitor.py%%'" get processid ^| findstr /r "[0-9]"') do (
    echo    Feed monitor started (PID: %%a)
    echo %%a > .monitor.pid
)
echo    Logs: feed_monitor.log
echo.

REM Wait for monitor to initialize
echo Waiting for feed monitor to initialize...
timeout /t 2 /nobreak >NUL

REM Start display viewer in background
echo Starting display viewer...
start "InkhavenDisplayViewer" /B cmd /c "uv run -m display_viewer > display_viewer.log 2>&1"
timeout /t 1 /nobreak >NUL

REM Get PID of display viewer
for /f "tokens=2" %%a in ('wmic process where "commandline like '%%display_viewer.py%%'" get processid ^| findstr /r "[0-9]"') do (
    echo    Display viewer started (PID: %%a)
    echo %%a > .viewer.pid
)
echo    Logs: display_viewer.log
echo.

echo ==========================================
echo Inkhaven Feed Viewer is running!
echo ==========================================
echo.
echo Monitor logs: type feed_monitor.log
echo Viewer logs:  type display_viewer.log
echo.
echo To view logs continuously: powershell Get-Content feed_monitor.log -Wait
echo To stop: kill.bat
echo.
