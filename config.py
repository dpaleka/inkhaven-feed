"""
Configuration file for Inkhaven Feed Viewer
All timing, sizing, and behavior settings in one place
"""

import platform

# ==============================================================================
# FEED MONITORING SETTINGS
# ==============================================================================

# URL of the Inkhaven feed to monitor
FEED_URL = "https://www.inkhaven.blog/feed.json"

# How often the feed_monitor.py script checks for new posts (in seconds)
# Lower = more frequent checks, higher = less frequent checks
# Recommended: 30-60 seconds
FEED_CHECK_INTERVAL = 30


# ==============================================================================
# BROWSER SETTINGS
# ==============================================================================

# Which browser to use: "chrome" (system Chrome) or "chromium" (Playwright's)
# Chrome gives you a more familiar browser experience
# Use "chromium" if Chrome isn't installed or has issues
BROWSER_TYPE = "chromium"


# ==============================================================================
# DISPLAY TIMING SETTINGS
# ==============================================================================

# How long to display each post before moving to the next (in seconds)
# This is the default time - you can always skip earlier with the skip button
# Recommended: 60-120 seconds
TIME_PER_POST = 10

# Maximum time to spend on any single post (in seconds)
# Safety limit to prevent getting stuck on one post forever
# Recommended: 300-600 seconds (5-10 minutes)
MAX_TIME_PER_POST = 300

# How often to check if the queue file has been updated with new posts (in seconds)
# The display viewer periodically checks for new posts added by the monitor
# Lower = more responsive, higher = less CPU usage
# Recommended: 5-10 seconds
QUEUE_CHECK_INTERVAL = 5


# ==============================================================================
# SCROLLING BEHAVIOR
# ==============================================================================

# How many pixels to scroll per step
# Lower = slower, smoother scrolling (more relaxed reading)
# Higher = faster scrolling (scan content quickly)
# Can use fractional values like 0.5 for very slow scrolling
# Recommended: 0.3-3 pixels
SCROLL_SPEED = 0.3  # Very slow, relaxed reading pace

# Time between each scroll step (in seconds)
# Lower = faster scrolling, higher = slower scrolling
# Recommended: 0.05-0.1 seconds
SCROLL_INTERVAL = 0.01  # Very smooth updates


# ==============================================================================
# BROWSER WINDOW SETTINGS
# ==============================================================================

# Detect platform
IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"

# Window dimensions (in pixels)
# Platform-specific sizing for optimal display
if IS_WINDOWS:
    # Windows with 3m diagonal screen - needs a bit more than half
    WINDOW_WIDTH = 1100   # More than half of typical Windows display
    WINDOW_HEIGHT = 1400  # Taller for better viewing
elif IS_MAC:
    # macOS - half screen width for side-by-side viewing
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 1200
else:
    # Default for Linux and other platforms
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 1200

# Window position on screen (in pixels from top-left corner)
# 0,0 = top-left corner of your screen
# Adjust to position the window where you want it
WINDOW_POSITION_X = 0
WINDOW_POSITION_Y = 0


# ==============================================================================
# FILE PATHS
# ==============================================================================

# JSON file containing the queue of posts to display
# Written by feed_monitor.py, read by display_viewer.py
QUEUE_FILE = "post_queue.json"

# JSON file tracking which posts have been seen before
# Used by feed_monitor.py to detect new posts
SEEN_POSTS_FILE = "seen_posts.json"


# ==============================================================================
# PAGE LOADING SETTINGS
# ==============================================================================

# Maximum time to wait for a page to load (in milliseconds)
# If a page takes longer than this, it will timeout and skip
# Recommended: 10000-20000 ms (10-20 seconds)
PAGE_LOAD_TIMEOUT = 15000

# Time to wait after page loads before starting to scroll (in seconds)
# Gives JavaScript time to render and images time to load
# Recommended: 1-3 seconds
PAGE_SETTLE_TIME = 2
