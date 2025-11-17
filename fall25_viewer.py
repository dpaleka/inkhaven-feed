#!/usr/bin/env python3
"""
Inkhaven Fall 25 Viewer
Opens the Fall 25 page and auto-refreshes every 30 seconds
"""

import asyncio
import sys
from playwright.async_api import async_playwright

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_POSITION_X,
    WINDOW_POSITION_Y,
    PAGE_LOAD_TIMEOUT,
    BROWSER_TYPE,
)

FALL25_URL = "https://www.inkhaven.blog/fall-25"
REFRESH_INTERVAL = 30  # seconds
ZOOM_LEVEL = 0.67  # 67% zoom (zoom out)


async def run():
    """Main run loop"""
    async with async_playwright() as p:
        print("=" * 60)
        print("Inkhaven Fall 25 Viewer")
        print("=" * 60)
        print(f"URL: {FALL25_URL}")
        print(f"Refresh interval: {REFRESH_INTERVAL}s")
        print(f"Launching {BROWSER_TYPE} browser...")
        print("=" * 60)
        print()

        # Select browser type
        if BROWSER_TYPE == "chrome":
            browser_engine = p.chromium
            browser_args = [
                '--disable-blink-features=AutomationControlled',
                f'--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}',
                f'--window-position={WINDOW_POSITION_X},{WINDOW_POSITION_Y}'
            ]
        else:
            browser_engine = p.chromium
            browser_args = [
                f'--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}',
                f'--window-position={WINDOW_POSITION_X},{WINDOW_POSITION_Y}'
            ]

        browser = await browser_engine.launch(
            headless=False,
            channel="chrome" if BROWSER_TYPE == "chrome" else None,
            args=browser_args
        )

        # Create page with no viewport restrictions
        page = await browser.new_page(viewport=None, no_viewport=True)

        try:
            refresh_count = 0
            while True:
                refresh_count += 1
                print(f"[Refresh #{refresh_count}] Loading {FALL25_URL}...")

                try:
                    await page.goto(FALL25_URL, wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)

                    # Apply zoom level
                    await page.evaluate(f"document.body.style.zoom = {ZOOM_LEVEL}")
                    print(f"✅ Page loaded successfully (zoom: {int(ZOOM_LEVEL * 100)}%)")
                except Exception as e:
                    print(f"❌ Error loading page: {e}")

                # Wait for next refresh
                print(f"⏱️  Waiting {REFRESH_INTERVAL}s until next refresh...")
                print()
                await asyncio.sleep(REFRESH_INTERVAL)

        except KeyboardInterrupt:
            print("\n\n⏹️  Viewer stopped by user")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run())
