#!/usr/bin/env python3
"""
Inkhaven Display Viewer
Displays posts from the post_queue.json file in a browser window with continuous scrolling.
Feed monitoring is handled separately by feed_monitor.py.
"""

import asyncio
import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from playwright.async_api import async_playwright, Page
from config import (
    SCROLL_SPEED,
    SCROLL_INTERVAL,
    TIME_PER_POST,
    MAX_TIME_PER_POST,
    QUEUE_FILE,
    QUEUE_CHECK_INTERVAL,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_POSITION_X,
    WINDOW_POSITION_Y,
    PAGE_LOAD_TIMEOUT,
    PAGE_SETTLE_TIME,
    BROWSER_TYPE,
)


class DisplayViewer:
    """
    Displays posts with intelligent selection:
    - Prioritizes new/unseen posts
    - Weighted random selection favoring recent posts
    - Still shows older posts occasionally
    """

    def __init__(self):
        self.queue_file = Path(QUEUE_FILE)
        self.posts = []  # All available posts
        self.post_history = {}  # Track when each post was last shown: {post_id: timestamp}
        self.skip_requested = False  # Flag to skip current post

    def load_queue(self):
        """Load posts from the queue file"""
        try:
            if not self.queue_file.exists():
                print(f"Queue file {self.queue_file} not found. Waiting for posts...")
                return []

            with open(self.queue_file, 'r') as f:
                posts = json.load(f)

            print(f"Loaded {len(posts)} posts from queue")
            return posts
        except json.JSONDecodeError as e:
            print(f"Error parsing queue file: {e}")
            return []
        except Exception as e:
            print(f"Error loading queue: {e}")
            return []

    def save_queue(self, posts):
        """Save the updated queue back to the file"""
        try:
            with open(self.queue_file, 'w') as f:
                json.dump(posts, f, indent=2)
        except Exception as e:
            print(f"Error saving queue: {e}")

    def mark_post_as_displayed(self, post_id):
        """Mark a post as displayed by recording current timestamp"""
        if post_id:
            self.post_history[post_id] = time.time()

    def calculate_post_weight(self, post):
        """
        Calculate selection weight for a post based on:
        1. Recency of post (newer = higher weight, exponential decay)
        2. Time since last shown (longer ago = higher weight)

        No special priority for unseen posts - they'll naturally show up
        if they're recent. Brand new posts are handled separately by
        the feed monitor (added to front of queue).
        """
        post_id = post.get("id")

        # Factor 1: Recency of post (exponential decay based on age)
        try:
            post_date_str = post.get("date_modified", "")
            post_date = datetime.fromisoformat(post_date_str.replace('Z', '+00:00'))
            days_old = (datetime.now(post_date.tzinfo) - post_date).days
            # Exponential decay: newer posts get higher weight
            recency_weight = 2 ** (-days_old / 30)  # Halves every 30 days
        except:
            recency_weight = 0.1  # Default low weight if date parsing fails

        # Factor 2: Time since last shown
        last_shown = self.post_history.get(post_id, 0)
        if last_shown > 0:
            minutes_since_shown = (time.time() - last_shown) / 60
            # Posts shown recently get lower weight
            time_weight = min(minutes_since_shown / 60, 10)  # Caps at 10 after 10 hours
        else:
            # Never shown - just use recency weight
            time_weight = 1.0

        # Combine factors
        total_weight = recency_weight * (1 + time_weight)
        return max(total_weight, 0.01)  # Minimum weight to keep all posts in pool

    def get_next_post(self):
        """
        Select next post using weighted random selection.
        Prioritizes unseen, recent, and not-recently-shown posts.
        """
        if not self.posts:
            return None

        # Calculate weights for all posts
        weights = [self.calculate_post_weight(post) for post in self.posts]

        # Weighted random selection
        selected_post = random.choices(self.posts, weights=weights, k=1)[0]

        return selected_post

    async def scroll_page(self, page: Page, duration: float):
        """
        Continuously scroll the page for a given duration.
        Scrolls down slowly and returns to top when reaching bottom.
        Checks for skip button clicks.
        """
        start_time = time.time()

        while time.time() - start_time < duration:
            # Check if skip button was clicked
            try:
                skip_clicked = await page.evaluate("""
                    () => {
                        const btn = document.getElementById('inkhaven-skip-btn');
                        return btn && btn.getAttribute('data-skip-clicked') === 'true';
                    }
                """)
                if skip_clicked:
                    print("⏭️  Skip requested!")
                    return  # Exit scrolling early
            except:
                pass  # Ignore errors checking button state

            # Scroll down by SCROLL_SPEED pixels
            await page.evaluate(f"window.scrollBy(0, {SCROLL_SPEED})")
            await asyncio.sleep(SCROLL_INTERVAL)

            # Check if we've reached the bottom
            is_at_bottom = await page.evaluate("""
                () => {
                    return (window.innerHeight + window.scrollY) >= document.body.scrollHeight - 100;
                }
            """)

            if is_at_bottom:
                # Scroll back to top and continue
                await page.evaluate("window.scrollTo(0, 0)")
                await asyncio.sleep(0.5)

    async def display_post(self, page: Page, post):
        """Navigate to and display a post"""
        url = post.get("url")
        title = post.get("title", "Untitled")
        author = post.get("author", {}).get("name", "Unknown")
        post_id = post.get("id")

        print(f"\n{'='*60}")
        print(f"Loading: {title}")
        print(f"Author: {author}")
        print(f"URL: {url}")
        print(f"{'='*60}\n")

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
            await asyncio.sleep(PAGE_SETTLE_TIME)  # Let the page settle

            # Add a skip button overlay
            await self.add_skip_button(page)

            # Mark this post as displayed
            self.mark_post_as_displayed(post_id)
        except Exception as e:
            print(f"Error loading page: {e}")

    async def add_skip_button(self, page: Page):
        """Add a floating skip button to the page"""
        try:
            await page.evaluate("""
                () => {
                    // Remove any existing skip button
                    const existing = document.getElementById('inkhaven-skip-btn');
                    if (existing) existing.remove();

                    // Create skip button
                    const btn = document.createElement('button');
                    btn.id = 'inkhaven-skip-btn';
                    btn.innerHTML = '⏭';
                    btn.style.cssText = `
                        position: fixed;
                        top: 30px;
                        right: 30px;
                        z-index: 999999;
                        padding: 12px 16px;
                        font-size: 20px;
                        background: rgba(255, 255, 255, 0.85);
                        color: #64748b;
                        border: 1px solid rgba(226, 232, 240, 0.8);
                        border-radius: 50px;
                        cursor: pointer;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                        backdrop-filter: blur(8px);
                        transition: all 0.25s ease;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                        opacity: 0.6;
                    `;

                    btn.onmouseover = () => {
                        btn.style.opacity = '1';
                        btn.style.transform = 'translateY(-2px)';
                        btn.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
                        btn.style.background = 'rgba(255, 255, 255, 0.95)';
                        btn.style.color = '#475569';
                    };
                    btn.onmouseout = () => {
                        btn.style.opacity = '0.6';
                        btn.style.transform = 'translateY(0)';
                        btn.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
                        btn.style.background = 'rgba(255, 255, 255, 0.85)';
                        btn.style.color = '#64748b';
                    };

                    btn.onclick = () => {
                        btn.setAttribute('data-skip-clicked', 'true');
                        btn.innerHTML = '✓';
                        btn.style.background = 'rgba(16, 185, 129, 0.9)';
                        btn.style.color = 'white';
                        btn.style.opacity = '1';
                    };

                    document.body.appendChild(btn);
                }
            """)
        except Exception as e:
            print(f"Error adding skip button: {e}")

    async def run(self):
        """Main run loop"""
        async with async_playwright() as p:
            # Launch browser with custom window size (half screen width)
            print(f"Launching {BROWSER_TYPE} browser...")

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

            # Create page with no viewport restrictions (full width rendering)
            # This allows the page to use the full window width
            page = await browser.new_page(viewport=None, no_viewport=True)

            # Load initial posts from queue
            print("Loading posts from queue...")
            self.posts = self.load_queue()

            # Wait for posts if queue is empty
            while not self.posts:
                print("Waiting for posts to appear in queue...")
                await asyncio.sleep(QUEUE_CHECK_INTERVAL)
                self.posts = self.load_queue()

            print(f"Starting display with {len(self.posts)} posts")

            # Display the first post
            current_post = self.get_next_post()
            if current_post:
                await self.display_post(page, current_post)

            last_queue_check = time.time()
            last_post_change = time.time()

            try:
                while True:
                    current_time = time.time()

                    # Periodically check for queue updates
                    if current_time - last_queue_check >= QUEUE_CHECK_INTERVAL:
                        new_posts = self.load_queue()
                        if new_posts and len(new_posts) != len(self.posts):
                            print(f"Queue updated: {len(new_posts)} posts available")
                            self.posts = new_posts
                            # Reset index to start from beginning with new posts
                            self.current_post_index = 0
                        last_queue_check = current_time

                    # Switch posts after TIME_PER_POST seconds, but enforce MAX_TIME_PER_POST
                    time_on_current_post = current_time - last_post_change
                    should_switch = (
                        time_on_current_post >= TIME_PER_POST or
                        time_on_current_post >= MAX_TIME_PER_POST
                    )

                    if should_switch:
                        # Get next post
                        next_post = self.get_next_post()
                        if next_post:
                            await self.display_post(page, next_post)
                            last_post_change = current_time
                        else:
                            # No posts available, reload queue
                            print("No posts available. Reloading queue...")
                            self.posts = self.load_queue()
                            if self.posts:
                                next_post = self.get_next_post()
                                if next_post:
                                    await self.display_post(page, next_post)
                                    last_post_change = current_time
                            else:
                                # Still no posts, wait a bit
                                await asyncio.sleep(QUEUE_CHECK_INTERVAL)
                                continue

                    # Check if skip button was clicked
                    try:
                        skip_clicked = await page.evaluate("""
                            () => {
                                const btn = document.getElementById('inkhaven-skip-btn');
                                return btn && btn.getAttribute('data-skip-clicked') === 'true';
                            }
                        """)
                        if skip_clicked:
                            print("⏭️  Skip button clicked! Moving to next post...")
                            # Get next post
                            next_post = self.get_next_post()
                            if next_post:
                                await self.display_post(page, next_post)
                                last_post_change = current_time
                            continue
                    except:
                        pass  # Ignore errors checking button state

                    # Continuously scroll for a short duration
                    scroll_duration = min(1.0, TIME_PER_POST - (current_time - last_post_change))
                    if scroll_duration > 0:
                        await self.scroll_page(page, scroll_duration)

                    await asyncio.sleep(0.1)

            except KeyboardInterrupt:
                print("\n\nShutting down...")
            finally:
                await browser.close()


if __name__ == "__main__":
    print("="*60)
    print("Inkhaven Display Viewer")
    print("="*60)
    print(f"Queue file: {QUEUE_FILE}")
    print(f"Time per post: {TIME_PER_POST}s (max {MAX_TIME_PER_POST}s)")
    print(f"Scroll speed: {SCROLL_SPEED}px every {SCROLL_INTERVAL}s")
    print("="*60)

    viewer = DisplayViewer()
    asyncio.run(viewer.run())
