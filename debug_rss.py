#!/usr/bin/env python3
"""
Debug script to see what's in your RSS feed
Run with: python3 debug_rss.py
"""

import os
import feedparser
from fetch_rss import parse_date, get_domain

def debug_rss():
    RSS_FEED_URL = os.environ.get("RSS_FEED_URL", "[INSERT YOUR RSS FEED URL]")

    if RSS_FEED_URL == "[INSERT YOUR RSS FEED URL]":
        print("❌ ERROR: Please set RSS_FEED_URL environment variable")
        print("Example: export RSS_FEED_URL='https://your-feed-url.com/rss'")
        return

    print(f"📡 Fetching RSS feed from: {RSS_FEED_URL}")
    print("=" * 80)

    feed = feedparser.parse(RSS_FEED_URL)

    if feed.bozo:
        print(f"⚠️  Warning: Feed might have issues: {feed.bozo_exception}")
        print()

    print(f"✅ Found {len(feed.entries)} items in feed")
    print()

    # Show first 3 items in detail
    for i, entry in enumerate(feed.entries[:3], 1):
        print(f"\n{'=' * 80}")
        print(f"ITEM {i}")
        print(f"{'=' * 80}")

        print(f"\nTitle: {entry.get('title', 'NO TITLE')}")
        print(f"Link: {entry.get('link', 'NO LINK')}")
        print(f"Date: {parse_date(entry)}")
        print(f"Source: {get_domain(entry.get('link', ''))}")

        # Check all possible description fields
        print("\n--- Available Description Fields ---")

        if hasattr(entry, "summary"):
            print(f"\n✅ summary field exists ({len(entry.summary)} chars):")
            print(f"   {entry.summary[:200]}...")
        else:
            print("\n❌ No 'summary' field")

        if hasattr(entry, "description"):
            print(f"\n✅ description field exists ({len(entry.description)} chars):")
            print(f"   {entry.description[:200]}...")
        else:
            print("\n❌ No 'description' field")

        if hasattr(entry, "content"):
            print(f"\n✅ content field exists:")
            if isinstance(entry.content, list):
                for j, c in enumerate(entry.content):
                    val = c.get("value", "")
                    print(f"   Content[{j}] ({len(val)} chars): {val[:200]}...")
        else:
            print("\n❌ No 'content' field")

        # Show what we'll actually save
        import re
        from html import unescape

        description = ""
        if hasattr(entry, "summary"):
            description = entry.summary
        elif hasattr(entry, "description"):
            description = entry.description
        elif hasattr(entry, "content"):
            if isinstance(entry.content, list) and len(entry.content) > 0:
                description = entry.content[0].get("value", "")

        # Clean it
        description = re.sub(r'<br\s*/?>', '\n', description)
        description = re.sub(r'<[^>]+>', ' ', description)
        description = unescape(description)
        description = re.sub(r'\s+', ' ', description)
        description = description.strip()

        print("\n--- Cleaned Description (what will be saved) ---")
        print(f"{description[:300]}...")
        print()

    print("\n" + "=" * 80)
    print(f"✅ Debug complete! Showing first 3 of {len(feed.entries)} items")
    print("=" * 80)

if __name__ == "__main__":
    debug_rss()
