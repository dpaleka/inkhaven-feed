#!/bin/bash

# Inkhaven Feed Viewer - Startup Script
# Starts both the feed monitor and display viewer

echo "=========================================="
echo "Starting Inkhaven Feed Viewer"
echo "=========================================="
echo ""

# Check if already running
if pgrep -f "feed_monitor.py" > /dev/null; then
    echo "⚠️  Feed monitor is already running!"
    echo "   Run ./kill.sh first to stop existing processes"
    exit 1
fi

if pgrep -f "display_viewer.py" > /dev/null; then
    echo "⚠️  Display viewer is already running!"
    echo "   Run ./kill.sh first to stop existing processes"
    exit 1
fi

# Start feed monitor in background
echo "🔍 Starting feed monitor..."
uv run -m feed_monitor > feed_monitor.log 2>&1 &
MONITOR_PID=$!
echo "   Feed monitor started (PID: $MONITOR_PID)"
echo "   Logs: feed_monitor.log"
echo ""

# Wait a moment for monitor to initialize
sleep 2

# Start display viewer in background
echo "🖥️  Starting display viewer..."
uv run -m display_viewer > display_viewer.log 2>&1 &
VIEWER_PID=$!
echo "   Display viewer started (PID: $VIEWER_PID)"
echo "   Logs: display_viewer.log"
echo ""

# Save PIDs to file for kill script
echo "$MONITOR_PID" > .monitor.pid
echo "$VIEWER_PID" > .viewer.pid

echo "=========================================="
echo "✅ Inkhaven Feed Viewer is running!"
echo "=========================================="
echo ""
echo "📊 Monitor logs: tail -f feed_monitor.log"
echo "🖥️  Viewer logs:  tail -f display_viewer.log"
echo ""
echo "To stop: ./kill.sh"
echo ""
