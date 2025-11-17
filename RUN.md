# How to Run the Inkhaven Feed Viewer

## Quickest Start - Single Command! ⚡

```bash
./run.sh
```

This starts both the feed monitor and display viewer in the background.

**To stop everything:**
```bash
./kill.sh
```

## How It Works

The app uses **intelligent post selection** instead of a simple queue:

### Feed Monitor
- Downloads ALL posts from the feed every 30 seconds
- Updates `post_queue.json` with the complete catalog
- Detects and announces new posts

### Display Viewer
- Uses **weighted random selection** to choose posts
- **Priority system:**
  1. **Unseen posts** - Massive priority (weight: 1000x)
  2. **Recent posts** - Higher weight (exponential decay)
  3. **Not recently shown** - Weight increases over time
- This means:
  - New posts appear very quickly
  - Recent posts show up more often
  - Old posts still appear occasionally
  - Variety without repetition

## Manual Start (Two Terminals)

### Terminal 1 - Feed Monitor
```bash
uv run -m feed_monitor
```

Logs to: `feed_monitor.log`

### Terminal 2 - Display Viewer
```bash
uv run -m display_viewer
```

Logs to: `display_viewer.log`

## Configuration

Edit `config.py` to customize:

### Common Adjustments

**Make window narrower/wider:**
```python
WINDOW_WIDTH = 600  # Default: 800
```

**Spend more/less time per post:**
```python
TIME_PER_POST = 120  # Default: 60 (seconds)
```

**Scroll slower/faster:**
```python
SCROLL_SPEED = 1  # Default: 2 (lower = slower)
```

**Check feed more/less often:**
```python
FEED_CHECK_INTERVAL = 60  # Default: 30 (seconds)
```

## Troubleshooting

**Browser closes immediately:**
- Make sure you have Chrome installed
- Or change `BROWSER_TYPE = "chromium"` in `config.py`

**Skip button not visible:**
- Look in the bottom-right corner (it's subtle!)
- It has 60% opacity until you hover over it
- Try hovering near the bottom-right

**No posts appear:**
- Check that `post_queue.json` exists and has posts
- Run `uv run -m feed_monitor` first to populate the queue

**Window too big/small:**
- Edit `WINDOW_WIDTH` and `WINDOW_HEIGHT` in `config.py`

## Stopping the App

Press `Ctrl+C` in the terminal where the script is running.

**Do NOT close the browser window** - this will cause errors. Always stop with `Ctrl+C`.
