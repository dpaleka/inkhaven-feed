# Inkhaven Feed Viewer

A smart feed reader that displays [Inkhaven](https://www.inkhaven.blog/) blog posts in a continuously scrolling browser window. Features intelligent post selection that prioritizes new and recent content while maintaining variety.

## Quick Start

### macOS / Linux

```bash
# Install uv (if you don't have it)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/dpaleka/inkhaven-feed.git
cd inkhaven-feed

# Install dependencies
uv sync

# Install Playwright browser
uv run -m playwright install chromium

# Start the app
./run.sh
```

### Windows

**Setup (one time):**
```powershell
# Install Git (if you don't have it)
winget install Git.Git

# Install uv (if you don't have it)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Restart PowerShell, then:
git clone https://github.com/dpaleka/inkhaven-feed.git
cd inkhaven-feed
uv sync
uv run -m playwright install chromium
```

**Running the app:**

Open **three PowerShell windows** in the `inkhaven-feed` directory.

**Window 1 - Feed Monitor:**
```powershell
uv run -m feed_monitor
```

**Window 2 - Display Viewer:**
```powershell
uv run -m display_viewer
```

**Window 3 - Fall 25 Viewer:**
```powershell
uv run -m fall25_viewer
```

Browser windows will open and start displaying Inkhaven posts.

**To stop:** Press `Ctrl+C` in each PowerShell window.

---

**To stop:**
- **macOS/Linux:** `./kill.sh`
- **Windows:** Press `Ctrl+C` in all three PowerShell windows

## What It Does

- **Monitors** the Inkhaven feed every 30 seconds for new posts
- **Displays** posts in a browser with smooth auto-scrolling
- **Prioritizes** recent posts and new content intelligently
- **Skip button** in top-right to jump to next post anytime
- **Runs continuously** in the background

## Features

### Smart Post Selection
- Brand new posts appear immediately (placed at front of queue)
- Recent posts show more frequently (exponential decay algorithm)
- Older posts still appear occasionally for variety
- Weighted random selection prevents repetition

### Customizable Display
- Auto-scrolling at configurable speed
- Window size optimized for side-by-side viewing (800x1200)
- Skip button to move to next post
- All settings in `config.py`

## Requirements

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installing uv (if needed)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or use pip:
```bash
pip install uv
```

## Usage

### Start Everything
```bash
./run.sh
```

This launches:
1. **Feed Monitor** - Checks for new posts every 30 seconds
2. **Display Viewer** - Shows posts in browser window
3. **Fall 25 Viewer** - Displays Fall 25 page with auto-refresh

All run in the background. Logs saved to:
- `feed_monitor.log`
- `display_viewer.log`
- `fall25_viewer.log`

### Stop Everything
```bash
./kill.sh
```

Cleanly stops both processes.

### Manual Control

**Start feed monitor only:**
```bash
uv run -m feed_monitor
```

**Start display viewer only:**
```bash
uv run -m display_viewer
```

**View Fall 25 page (auto-refreshes every 30s):**
```bash
uv run -m fall25_viewer
```

**Stop with Ctrl+C** in each terminal.

## Configuration

Edit `config.py` to customize behavior:

### Common Settings

**Display time per post:**
```python
TIME_PER_POST = 60  # seconds (default: 60)
```

**Scroll speed:**
```python
SCROLL_SPEED = 2  # pixels per step (lower = slower)
```

**Window size:**
```python
WINDOW_WIDTH = 800   # pixels
WINDOW_HEIGHT = 1200 # pixels
```

**Feed check frequency:**
```python
FEED_CHECK_INTERVAL = 30  # seconds
```

**Browser type:**
```python
BROWSER_TYPE = "chromium"  # or "chrome"
```

See `config.py` for all available settings with detailed comments.

## How It Works

### Architecture

```
┌─────────────────────┐
│   Feed Monitor      │  Checks feed every 30s
│                     │  ↓
│  • Downloads feed   │  Detects new posts
│  • Detects new      │  ↓
│  • Updates queue    │  Places new posts at front
└─────────────────────┘
          ↓
    post_queue.json ← All posts (new ones first)
          ↓
┌─────────────────────┐
│  Display Viewer     │  Reads from queue
│                     │  ↓
│  • Weighted random  │  Selects next post
│  • Opens browser    │  (prioritizes recent)
│  • Auto-scrolls     │  ↓
│  • Shows skip btn   │  Displays in browser
└─────────────────────┘
```

### Post Selection Algorithm

Posts are selected using weighted randomness:

1. **Recency Weight**: Exponential decay (halves every 30 days)
   - Today's post: weight = 1.0
   - 30-day-old post: weight = 0.5
   - 60-day-old post: weight = 0.25

2. **Time Since Last Shown**: Linear increase
   - Just shown: low weight
   - Not shown for hours: higher weight
   - Caps at 10x after 10 hours

3. **New Posts**: Placed at front of queue
   - Combined with recency weight
   - Appear very quickly (but not artificially boosted)

This ensures:
- ✅ New posts appear fast
- ✅ Recent content gets priority
- ✅ Variety from older posts
- ✅ Natural, balanced distribution

## Files Created

- `post_queue.json` - All posts from feed (new ones first)
- `seen_posts.json` - Tracks which posts have been discovered
- `feed_monitor.log` - Feed monitor output
- `display_viewer.log` - Display viewer output
- `fall25_viewer.log` - Fall 25 viewer output
- `.monitor.pid`, `.viewer.pid`, `.fall25.pid` - Process IDs for kill script

## Troubleshooting

**Browser closes immediately:**
- Check that Chromium is installed: `uv run -m playwright install chromium`
- Or switch to Chrome in `config.py`: `BROWSER_TYPE = "chrome"`

**Skip button not visible:**
- Look in top-right corner (it's subtle with 60% opacity)
- Hover over it to make it fully visible

**No posts appear:**
- Ensure internet connection is working
- Check `feed_monitor.log` for errors
- Verify feed URL is accessible: https://www.inkhaven.blog/feed.json

**Processes won't stop:**
- Run `./kill.sh` multiple times
- Or manually: `pkill -f feed_monitor.py && pkill -f display_viewer.py`

## Development

### Project Structure

```
inkhaven-feed/
├── config.py              # All configuration settings
├── feed_monitor.py        # Monitors feed for new posts
├── display_viewer.py      # Displays posts in browser
├── fall25_viewer.py       # Views Fall 25 page with auto-refresh
├── run.sh                 # Start script (macOS/Linux)
├── kill.sh                # Stop script (macOS/Linux)
├── run.bat                # Start script (Windows)
├── kill.bat               # Stop script (Windows)
├── pyproject.toml         # Python dependencies
├── README.md              # This file
└── RUN.md                 # Detailed usage guide
```

### Dependencies

- **playwright** - Browser automation
- **httpx** - HTTP client for feed downloads

## Contributing

Issues and pull requests welcome!

## License

MIT License

## Acknowledgments

Built for [Inkhaven](https://www.inkhaven.blog/), a residency program for bloggers and writers.
