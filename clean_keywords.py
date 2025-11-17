#!/usr/bin/env python3
"""
Clean up excluded keywords from feed.json
Usage: python3 clean_keywords.py
"""

import json

# Excluded keywords (too generic for haptics research)
EXCLUDED_KEYWORDS = {'haptic', 'haptics', 'vibration', 'vibrations', 'tactile'}

def clean_keywords():
    """Remove excluded keywords from feed.json"""

    # Load feed
    with open('feed.json', 'r', encoding='utf-8') as f:
        items = json.load(f)

    total_removed = 0
    items_updated = 0

    for item in items:
        if 'keywords' in item and item['keywords']:
            original_count = len(item['keywords'])
            item['keywords'] = [
                kw for kw in item['keywords']
                if kw.lower() not in EXCLUDED_KEYWORDS
            ]
            removed = original_count - len(item['keywords'])
            if removed > 0:
                total_removed += removed
                items_updated += 1

    # Save cleaned feed
    with open('feed.json', 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    print(f"✅ Cleaned {total_removed} keywords from {items_updated} items")
    print(f"   Excluded: {', '.join(sorted(EXCLUDED_KEYWORDS))}")

if __name__ == "__main__":
    clean_keywords()
