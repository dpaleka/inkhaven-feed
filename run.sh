#!/bin/bash

# Inkhaven Feed Viewer - Startup Script
# Starts the feed monitor, display viewer, and fall25 viewer

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

if pgrep -f "fall25_viewer.py" > /dev/null; then
    echo "⚠️  Fall 25 viewer is already running!"
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

# Start fall25 viewer in background
echo "📅 Starting Fall 25 viewer..."
uv run -m fall25_viewer > fall25_viewer.log 2>&1 &
FALL25_PID=$!
echo "   Fall 25 viewer started (PID: $FALL25_PID)"
echo "   Logs: fall25_viewer.log"
echo ""

# Save PIDs to file for kill script
echo "$MONITOR_PID" > .monitor.pid
echo "$VIEWER_PID" > .viewer.pid
echo "$FALL25_PID" > .fall25.pid

echo "=========================================="
echo "✅ Inkhaven Feed Viewer is running!"
echo "=========================================="
echo ""
echo "📊 Monitor logs:  tail -f feed_monitor.log"
echo "🖥️  Viewer logs:   tail -f display_viewer.log"
echo "📅 Fall 25 logs:  tail -f fall25_viewer.log"
echo ""
echo "To stop: ./kill.sh"
echo ""
