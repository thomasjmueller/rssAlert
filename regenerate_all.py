#!/usr/bin/env python3
"""
Clear AI summaries and keywords from all items to trigger regeneration
Usage: python3 regenerate_all.py
"""

import json
import shutil
from datetime import datetime

def regenerate_all():
    """Clear AI data from all items"""

    # Backup first
    backup_name = f"feed.json.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy('feed.json', backup_name)
    print(f"📦 Backup created: {backup_name}")

    # Load feed
    with open('feed.json', 'r', encoding='utf-8') as f:
        items = json.load(f)

    cleared_count = 0
    for item in items:
        if 'ai_summary' in item or 'keywords' in item:
            item.pop('ai_summary', None)
            item['keywords'] = []
            cleared_count += 1

    # Save
    with open('feed.json', 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    print(f"✅ Cleared AI data from {cleared_count} items")
    print(f"📊 Total items ready for processing: {len(items)}")
    print(f"\nNext steps:")
    print(f"  export GEMINI_API_KEY='your-key'")
    print(f"  python3 summarize_with_gemini.py")
    print(f"\nNote: With 10 items/run and 7s delay, it will take:")
    print(f"  - ~{len(items) * 7 // 60} minutes to process all {len(items)} items")
    print(f"  - Or ~{(len(items) + 9) // 10} separate runs")

if __name__ == "__main__":
    regenerate_all()
