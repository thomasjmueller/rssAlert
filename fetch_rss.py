#!/usr/bin/env python3
"""
RSS Feed Fetcher and Archiver
Fetches RSS feed, deduplicates, and saves to feed.json
"""

import json
import os
from datetime import datetime
from urllib.parse import urlparse
import feedparser
import requests


def get_domain(url):
    """Extract clean domain name from URL (without www and suffix)"""
    from urllib.parse import parse_qs
    try:
        # Handle Google redirect URLs
        if 'google.com/url' in url:
            parsed_google = urlparse(url)
            query_params = parse_qs(parsed_google.query)
            # Extract the actual destination URL from 'url' parameter
            if 'url' in query_params:
                url = query_params['url'][0]

        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path

        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]

        # Remove common TLD suffixes (.com, .org, .net, etc.)
        # Split by last dot and take everything before it
        parts = domain.split('.')
        if len(parts) > 1:
            # Keep only the main domain name (remove TLD)
            domain = parts[0]

        return domain if domain else "unknown"
    except Exception:
        return "unknown"


def load_existing_feed(filename="feed.json"):
    """Load existing feed data"""
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load existing feed: {e}")
            return []
    return []


def parse_date(entry):
    """Parse date from feed entry"""
    # Try different date fields
    date_fields = ["published_parsed", "updated_parsed", "created_parsed"]
    for field in date_fields:
        if hasattr(entry, field) and getattr(entry, field):
            try:
                time_struct = getattr(entry, field)
                return datetime(*time_struct[:6]).isoformat()
            except Exception:
                continue

    # Fallback to current date if no valid date found
    return datetime.now().isoformat()


def fetch_rss(feed_url):
    """Fetch and parse RSS feed"""
    print(f"Fetching RSS feed from: {feed_url}")

    # Fetch the feed
    feed = feedparser.parse(feed_url)

    if feed.bozo:
        print(f"Warning: Feed might have issues: {feed.bozo_exception}")

    items = []
    for entry in feed.entries:
        # Extract link
        link = entry.get("link", "")
        if not link:
            continue

        # Extract title
        title = entry.get("title", "Untitled")

        # Parse date
        date = parse_date(entry)

        # Get source domain
        source = get_domain(link)

        # Extract description/summary
        # Google Alerts uses 'content', other feeds may use 'summary' or 'description'
        description = ""
        if hasattr(entry, "content") and isinstance(entry.content, list) and len(entry.content) > 0:
            # Google Alerts and Atom feeds use content
            description = entry.content[0].get("value", "")
        elif hasattr(entry, "summary"):
            description = entry.summary
        elif hasattr(entry, "description"):
            description = entry.description

        # Clean up HTML tags from description
        import re
        from html import unescape

        # Remove HTML tags but preserve spacing
        description = re.sub(r'<br\s*/?>', '\n', description)  # Convert <br> to newlines
        description = re.sub(r'<[^>]+>', ' ', description)  # Remove all other tags
        description = unescape(description)  # Decode HTML entities like &amp; &nbsp;
        description = re.sub(r'\s+', ' ', description)  # Normalize whitespace
        description = description.strip()

        # Limit to first 300 characters for preview
        if len(description) > 300:
            description = description[:300].rsplit(' ', 1)[0] + '...'

        items.append({
            "title": title,
            "link": link,
            "date": date,
            "source": source,
            "description": description
        })

    print(f"Fetched {len(items)} items from feed")
    return items


def deduplicate_items(new_items, existing_items):
    """Deduplicate items by URL and title"""
    # Create sets of existing URLs and titles
    existing_urls = {item["link"] for item in existing_items}
    existing_titles = {item["title"] for item in existing_items}

    # Filter out duplicates (skip if URL or title already exists)
    unique_items = [
        item for item in new_items
        if item["link"] not in existing_urls and item["title"] not in existing_titles
    ]

    print(f"Found {len(unique_items)} new unique items")
    return unique_items


def save_feed(items, filename="feed.json"):
    """Save feed data to JSON file"""
    # Sort by date (newest first)
    items.sort(key=lambda x: x["date"], reverse=True)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(items)} items to {filename}")


def main():
    # RSS feed URLs - add your RSS feed URLs here
    RSS_FEED_URLS = [
        "https://www.reddit.com/search.rss?q=haptics&cId=eb95654f-ed4b-4d4b-bc90-34f89c315d08&iId=06497d47-4db9-46c6-a425-3776d68fd7f4",
        "https://www.google.com/alerts/feeds/13434099267717249872/5616231719166364050",
    ]

    # Backward compatibility: check for old single URL env var
    old_url = os.environ.get("RSS_FEED_URL", "")
    if old_url and old_url != "[INSERT YOUR RSS FEED URL]":
        RSS_FEED_URLS.append(old_url)

    # Can also load from environment variable (comma-separated)
    env_urls = os.environ.get("RSS_FEED_URLS", "")
    if env_urls:
        RSS_FEED_URLS.extend([url.strip() for url in env_urls.split(",") if url.strip()])

    if not RSS_FEED_URLS:
        print("Error: Please add RSS feed URLs to the RSS_FEED_URLS list or set RSS_FEED_URLS environment variable")
        print("Example: export RSS_FEED_URLS='https://example.com/feed.xml,https://another.com/rss'")
        return

    # Load existing feed
    existing_items = load_existing_feed()
    print(f"Loaded {len(existing_items)} existing items")

    # Fetch from all feeds
    all_new_items = []
    for feed_url in RSS_FEED_URLS:
        try:
            new_items = fetch_rss(feed_url)
            all_new_items.extend(new_items)
        except Exception as e:
            print(f"Error fetching {feed_url}: {e}")
            continue

    print(f"\nTotal fetched: {len(all_new_items)} items from {len(RSS_FEED_URLS)} feeds")

    # Deduplicate
    unique_new_items = deduplicate_items(all_new_items, existing_items)

    # Combine and save
    all_items = existing_items + unique_new_items
    save_feed(all_items)

    print("Done!")


if __name__ == "__main__":
    main()
