#!/usr/bin/env python3
"""
Fix source domains in feed.json by extracting real domains from Google redirect URLs
Usage: python3 fix_sources.py
"""

import json
from urllib.parse import urlparse, parse_qs


def get_domain(url):
    """Extract clean domain name from URL (without www and suffix)"""
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
        parts = domain.split('.')
        if len(parts) > 1:
            # Keep only the main domain name (remove TLD)
            domain = parts[0]

        return domain if domain else "unknown"
    except Exception:
        return "unknown"


def fix_sources():
    """Update source domains in feed.json"""

    # Load feed
    with open('feed.json', 'r', encoding='utf-8') as f:
        items = json.load(f)

    updated = 0

    for item in items:
        old_source = item.get('source', 'unknown')
        new_source = get_domain(item['link'])

        if old_source != new_source:
            item['source'] = new_source
            updated += 1
            print(f"✓ {old_source} → {new_source}: {item['title'][:50]}...")

    # Save updated feed
    with open('feed.json', 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Updated {updated} source domains")

if __name__ == "__main__":
    fix_sources()
