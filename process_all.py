#!/usr/bin/env python3
"""
Process all items until complete
Automatically runs summarize_with_gemini.py in a loop until all items have AI summaries
"""

import json
import os
import sys
import subprocess
import time

def count_remaining():
    """Count items without AI summaries"""
    try:
        with open('feed.json', 'r', encoding='utf-8') as f:
            items = json.load(f)
        return sum(1 for item in items if not item.get('ai_summary'))
    except Exception as e:
        print(f"Error reading feed.json: {e}")
        return 0

def main():
    # Check API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("   Run: export GEMINI_API_KEY='your-api-key'")
        sys.exit(1)

    print("🤖 Automated processing of all feed items")
    print("=" * 60)

    iteration = 0
    while True:
        iteration += 1
        remaining = count_remaining()

        if remaining == 0:
            print("\n" + "=" * 60)
            print("✅ All items processed successfully!")
            break

        print(f"\n🔄 Iteration {iteration}: {remaining} items remaining")
        print("-" * 60)

        # Run summarize_with_gemini.py
        try:
            result = subprocess.run(
                ['python3', 'summarize_with_gemini.py'],
                check=True,
                capture_output=False
            )
        except subprocess.CalledProcessError as e:
            print(f"\n⚠️  Error running summarize script: {e}")
            print("Stopping automated processing")
            sys.exit(1)

        # Check if there are more items to process
        new_remaining = count_remaining()

        if new_remaining == remaining:
            print("\n⚠️  No progress made in this iteration")
            print("This might indicate an issue. Check the output above.")
            break

        if new_remaining > 0:
            wait_time = 2  # Minimal wait between batches
            print(f"\n⏳ Waiting {wait_time} seconds before next batch...")
            time.sleep(wait_time)

    print("\n🎉 Processing complete!")

if __name__ == "__main__":
    main()
