@echo off
REM Inkhaven Feed Viewer - Startup Script
REM Starts both the feed monitor and display viewer

echo ==========================================
echo Starting Inkhaven Feed Viewer
echo ==========================================
echo.

REM Check if feed monitor is already running
tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq feed_monitor*" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo WARNING: Feed monitor may already be running!
    echo    Run kill.bat first to stop existing processes
    exit /b 1
)

REM Check more broadly for feed_monitor.py in command line
wmic process where "commandline like '%%feed_monitor.py%%'" get processid 2>NUL | findstr /r "[0-9]" >NUL
if "%ERRORLEVEL%"=="0" (
    echo WARNING: Feed monitor is already running!
    echo    Run kill.bat first to stop existing processes
    exit /b 1
)

REM Check for display viewer
wmic process where "commandline like '%%display_viewer.py%%'" get processid 2>NUL | findstr /r "[0-9]" >NUL
if "%ERRORLEVEL%"=="0" (
    echo WARNING: Display viewer is already running!
    echo    Run kill.bat first to stop existing processes
    exit /b 1
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
