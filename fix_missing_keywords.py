#!/usr/bin/env python3
"""
Fix items that have summaries but missing keywords
Usage: python3 fix_missing_keywords.py
"""

import json

def fix_missing_keywords():
    """Clear summaries for items missing keywords so they get reprocessed"""

    # Load feed
    with open('feed.json', 'r', encoding='utf-8') as f:
        items = json.load(f)

    # Find items with summary but no keywords
    items_to_fix = []
    for item in items:
        if item.get('ai_summary') and (not item.get('keywords') or len(item.get('keywords', [])) == 0):
            items_to_fix.append(item)

    if len(items_to_fix) == 0:
        print("✅ All items with summaries also have keywords!")
        return

    print(f"Found {len(items_to_fix)} items with summaries but no keywords:")
    for item in items_to_fix[:5]:
        print(f"  - {item['title'][:60]}...")

    # Clear their summaries so they get reprocessed
    for item in items_to_fix:
        item.pop('ai_summary', None)
        item['keywords'] = []

    # Save
    with open('feed.json', 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Cleared summaries for {len(items_to_fix)} items")
    print(f"Run: python3 process_all.py")

if __name__ == "__main__":
    fix_missing_keywords()
