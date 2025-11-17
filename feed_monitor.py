#!/usr/bin/env python3
"""
Inkhaven Feed Monitor

This script continuously monitors the Inkhaven blog feed for new posts.
It downloads the feed every 30 seconds, compares it to the previous version,
and maintains a queue of new posts for consumption by other processes.

Files created/managed:
- post_queue.json: Queue of new posts waiting to be displayed
- seen_posts.json: Record of all post IDs that have been encountered
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

import httpx
from config import FEED_URL, FEED_CHECK_INTERVAL, QUEUE_FILE, SEEN_POSTS_FILE


# Use config values
CHECK_INTERVAL = FEED_CHECK_INTERVAL
QUEUE_FILE = Path(QUEUE_FILE)
SEEN_POSTS_FILE = Path(SEEN_POSTS_FILE)


class FeedMonitor:
    """Monitors the Inkhaven feed and manages the post queue."""

    def __init__(self):
        self.seen_posts: Set[str] = self._load_seen_posts()
        self.queue: List[Dict] = self._load_queue()

    def _load_seen_posts(self) -> Set[str]:
        """Load the set of previously seen post IDs from disk."""
        if SEEN_POSTS_FILE.exists():
            try:
                with open(SEEN_POSTS_FILE, 'r') as f:
                    data = json.load(f)
                    print(f"📋 Loaded {len(data)} seen posts from {SEEN_POSTS_FILE}")
                    return set(data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Error loading seen posts: {e}")
                return set()
        else:
            print(f"📄 No seen posts file found, starting fresh")
            return set()

    def _save_seen_posts(self):
        """Save the set of seen post IDs to disk."""
        try:
            with open(SEEN_POSTS_FILE, 'w') as f:
                json.dump(sorted(list(self.seen_posts)), f, indent=2)
        except IOError as e:
            print(f"❌ Error saving seen posts: {e}")

    def _load_queue(self) -> List[Dict]:
        """Load the post queue from disk."""
        if QUEUE_FILE.exists():
            try:
                with open(QUEUE_FILE, 'r') as f:
                    queue = json.load(f)
                    print(f"📥 Loaded {len(queue)} posts from queue")
                    return queue
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Error loading queue: {e}")
                return []
        else:
            print(f"📄 No queue file found, starting with empty queue")
            return []

    def _save_queue(self):
        """Save the post queue to disk."""
        try:
            with open(QUEUE_FILE, 'w') as f:
                json.dump(self.queue, f, indent=2)
        except IOError as e:
            print(f"❌ Error saving queue: {e}")

    async def fetch_feed(self) -> Dict | None:
        """
        Download the feed from the Inkhaven blog.

        Returns:
            The parsed JSON feed, or None if there was an error.
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(FEED_URL)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"❌ HTTP error fetching feed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing feed JSON: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error fetching feed: {e}")
            return None

    def process_feed(self, feed: Dict):
        """
        Process the feed and update the queue with ALL posts.
        Brand new posts (detected this check) are placed at the front.

        Args:
            feed: The parsed JSON feed
        """
        if not feed or 'items' not in feed:
            print("⚠️  Invalid feed structure")
            return

        items = feed['items']
        new_posts = []
        existing_posts = []

        # Separate new posts from existing ones
        for item in items:
            post_id = item.get('id')
            if not post_id:
                continue

            # If this is a brand new post we haven't seen before
            if post_id not in self.seen_posts:
                # Mark when this post was discovered
                item['discovered_at'] = time.time()
                new_posts.append(item)
                self.seen_posts.add(post_id)
            else:
                existing_posts.append(item)

        # Build queue: new posts first, then existing posts
        # This ensures brand new posts get shown immediately
        self.queue = new_posts + existing_posts

        # Save updated queue and seen posts
        self._save_queue()
        if new_posts:
            self._save_seen_posts()

        # Report findings
        if new_posts:
            print(f"\n🎉 Found {len(new_posts)} new post(s)!")
            for post in new_posts:
                author = post.get('author', {}).get('name', 'Unknown')
                title = post.get('title', 'Untitled')
                print(f"   • \"{title}\" by {author}")
            print(f"   → New posts placed at front of queue for immediate display")
        else:
            print("✅ No new posts")

    async def run(self):
        """Main monitoring loop."""
        print("=" * 60)
        print("🔍 Inkhaven Feed Monitor Started")
        print(f"📡 Feed URL: {FEED_URL}")
        print(f"⏱️  Check interval: {CHECK_INTERVAL} seconds")
        print(f"📦 Queue file: {QUEUE_FILE.absolute()}")
        print(f"📝 Seen posts file: {SEEN_POSTS_FILE.absolute()}")
        print("=" * 60)
        print()

        iteration = 0
        while True:
            iteration += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Check #{iteration}: Fetching feed...")

            feed = await self.fetch_feed()
            if feed:
                print(f"✅ Feed downloaded successfully ({len(feed.get('items', []))} total posts)")
                self.process_feed(feed)
            else:
                print("⚠️  Failed to fetch feed, will retry next interval")

            # Show current queue status
            print(f"📊 Queue status: {len(self.queue)} post(s) waiting")
            print(f"📚 Total posts seen: {len(self.seen_posts)}")
            print()

            # Wait for next check
            await asyncio.sleep(CHECK_INTERVAL)


async def main():
    """Entry point for the feed monitor."""
    monitor = FeedMonitor()
    try:
        await monitor.run()
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitor stopped by user")
        print(f"Final status: {len(monitor.queue)} posts in queue, {len(monitor.seen_posts)} posts seen")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
