@echo off
REM Inkhaven Feed Viewer - Kill Script
REM Stops both the feed monitor and display viewer

echo ==========================================
echo Stopping Inkhaven Feed Viewer
echo ==========================================
echo.

set KILLED=0

REM Kill feed monitor by PID file
if exist .monitor.pid (
    set /p MONITOR_PID=<.monitor.pid
    echo Checking for feed monitor with PID: !MONITOR_PID!...
    tasklist /FI "PID eq !MONITOR_PID!" 2>NUL | find /I "python.exe">NUL
    if "!ERRORLEVEL!"=="0" (
        echo Stopping feed monitor (PID: !MONITOR_PID!)...
        taskkill /PID !MONITOR_PID! /F >NUL 2>&1
        set /a KILLED+=1
    )
    del .monitor.pid
)

REM Kill any remaining feed_monitor.py processes
for /f "tokens=2" %%a in ('wmic process where "commandline like '%%feed_monitor.py%%'" get processid 2^>NUL ^| findstr /r "[0-9]"') do (
    echo Found additional feed monitor process: %%a
    echo    Killing...
    taskkill /PID %%a /F >NUL 2>&1
    set /a KILLED+=1
)

REM Kill display viewer by PID file
if exist .viewer.pid (
    set /p VIEWER_PID=<.viewer.pid
    echo Checking for display viewer with PID: !VIEWER_PID!...
    tasklist /FI "PID eq !VIEWER_PID!" 2>NUL | find /I "python.exe">NUL
    if "!ERRORLEVEL!"=="0" (
        echo Stopping display viewer (PID: !VIEWER_PID!)...
        taskkill /PID !VIEWER_PID! /F >NUL 2>&1
        set /a KILLED+=1
    )
    del .viewer.pid
)

REM Kill any remaining display_viewer.py processes
for /f "tokens=2" %%a in ('wmic process where "commandline like '%%display_viewer.py%%'" get processid 2^>NUL ^| findstr /r "[0-9]"') do (
    echo Found additional display viewer process: %%a
    echo    Killing...
    taskkill /PID %%a /F >NUL 2>&1
    set /a KILLED+=1
)

echo.
if %KILLED% gtr 0 (
    echo Stopped %KILLED% process(es)
) else (
    echo No running processes found
)
echo.
