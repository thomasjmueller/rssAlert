#!/usr/bin/env python3
"""
Score post relevance using AI
Analyzes posts and adds relevance_level: low, mid, or high
"""

import json
import os
import sys
import time
from typing import List, Dict
import google.generativeai as genai


def setup_gemini():
    """Setup Gemini API"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("   Get your API key from: https://makersuite.google.com/app/apikey")
        print("   Then run: export GEMINI_API_KEY='your-api-key'")
        sys.exit(1)

    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-flash-latest')


def score_post(model, item: Dict) -> str:
    """Score a single post's relevance (low, mid, high)"""

    title = item.get('title', '')
    summary = item.get('ai_summary', '') or item.get('description', '')

    if not summary:
        return 'low'

    prompt = f"""Analyze this haptics-related post and rate its relevance level as LOW, MID, or HIGH based on these criteria:

HIGH relevance if it mentions:
- Haptic design tools or authoring software
- Developer APIs or SDKs for haptics
- Companies creating haptic experiences or content
- New devices with haptic playback capabilities

MID relevance if it:
- Discusses haptic technology or research
- Mentions haptic feedback in products
- Contains useful haptic industry information

LOW relevance if it:
- Only briefly mentions haptics
- Is not directly relevant to haptic development/design

Title: {title}

Summary: {summary}

Respond with ONLY one word: LOW, MID, or HIGH"""

    try:
        response = model.generate_content(prompt)
        result = response.text.strip().upper()

        # Validate response
        if result in ['HIGH', 'MID', 'LOW']:
            return result.lower()
        else:
            # Default to low if response is unclear
            print(f"  Warning: Unclear response '{result}', defaulting to low")
            return 'low'

    except Exception as e:
        print(f"  Error scoring post: {e}")
        return 'low'


def main():
    print("🎯 Scoring post relevance with AI")
    print("=" * 60)

    # Setup
    model = setup_gemini()

    # Load feed
    with open('feed.json', 'r', encoding='utf-8') as f:
        items = json.load(f)

    print(f"📊 Loaded {len(items)} items")

    # Find items to score (those without relevance_level or need re-scoring)
    items_to_score = [item for item in items if not item.get('relevance_level')]

    if len(items_to_score) == 0:
        print("✅ All items already have relevance scores!")
        print("   To re-score, delete the 'relevance_level' field from items in feed.json")
        return

    print(f"🔍 Scoring {len(items_to_score)} items...\n")

    # Score each item
    scored_count = {'high': 0, 'mid': 0, 'low': 0}

    for i, item in enumerate(items_to_score, 1):
        title = item.get('title', 'Untitled')[:60]
        print(f"[{i}/{len(items_to_score)}] {title}...")

        level = score_post(model, item)
        item['relevance_level'] = level
        scored_count[level] += 1

        print(f"  → {level.upper()}")

        # Rate limiting - wait between requests
        if i < len(items_to_score):
            time.sleep(1)  # 1 second between requests

    # Save
    with open('feed.json', 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("✅ Relevance scoring complete!")
    print(f"\n📈 Results:")
    print(f"   HIGH: {scored_count['high']} items")
    print(f"   MID:  {scored_count['mid']} items")
    print(f"   LOW:  {scored_count['low']} items")
    print(f"\n💾 Saved to feed.json")


if __name__ == "__main__":
    main()
