#!/bin/bash

# Inkhaven Feed Viewer - Kill Script
# Stops both the feed monitor and display viewer

echo "=========================================="
echo "Stopping Inkhaven Feed Viewer"
echo "=========================================="
echo ""

KILLED=0

# Kill feed monitor
if [ -f .monitor.pid ]; then
    MONITOR_PID=$(cat .monitor.pid)
    if ps -p $MONITOR_PID > /dev/null 2>&1; then
        echo "🔍 Stopping feed monitor (PID: $MONITOR_PID)..."
        kill $MONITOR_PID
        KILLED=$((KILLED + 1))
    fi
    rm .monitor.pid
fi

# Also kill by process name in case PID file is missing
MONITOR_PIDS=$(pgrep -f "feed_monitor.py")
if [ ! -z "$MONITOR_PIDS" ]; then
    echo "🔍 Found additional feed monitor processes: $MONITOR_PIDS"
    echo "   Killing..."
    pkill -f "feed_monitor.py"
    KILLED=$((KILLED + 1))
fi

# Kill display viewer
if [ -f .viewer.pid ]; then
    VIEWER_PID=$(cat .viewer.pid)
    if ps -p $VIEWER_PID > /dev/null 2>&1; then
        echo "🖥️  Stopping display viewer (PID: $VIEWER_PID)..."
        kill $VIEWER_PID
        KILLED=$((KILLED + 1))
    fi
    rm .viewer.pid
fi

# Also kill by process name in case PID file is missing
VIEWER_PIDS=$(pgrep -f "display_viewer.py")
if [ ! -z "$VIEWER_PIDS" ]; then
    echo "🖥️  Found additional display viewer processes: $VIEWER_PIDS"
    echo "   Killing..."
    pkill -f "display_viewer.py"
    KILLED=$((KILLED + 1))
fi

echo ""
if [ $KILLED -gt 0 ]; then
    echo "✅ Stopped $KILLED process(es)"
else
    echo "ℹ️  No running processes found"
fi
echo ""
