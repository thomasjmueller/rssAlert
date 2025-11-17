#!/usr/bin/env python3
"""
Generate haptic-focused summaries using Gemini API
Usage: python3 summarize_with_gemini.py
"""

import json
import os
import sys
import time
import requests
from urllib.parse import urlparse

try:
    import google.generativeai as genai
except ImportError:
    print("⚠️  google-generativeai not installed. Run: pip install google-generativeai")
    sys.exit(1)


def fetch_article_content(url, timeout=10):
    """Fetch article content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        # Return first 10000 characters to avoid token limits
        return response.text[:10000]
    except Exception as e:
        print(f"  ⚠️  Could not fetch {url}: {e}")
        return None


def generate_haptic_summary(title, description, url, api_key):
    """Generate a haptic-focused summary using Gemini API"""

    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

    # Fetch article content for better context
    article_content = fetch_article_content(url)

    # Build prompt
    prompt = f"""Analyze this article and create a concise summary (2-3 sentences) focused ONLY on haptic/tactile feedback content.

Title: {title}
Description: {description}

"""

    if article_content:
        prompt += f"Article Content (excerpt): {article_content[:3000]}\n\n"

    prompt += """Instructions:
- Focus exclusively on haptic, tactile, or touch feedback related content
- Be specific about haptic technologies, techniques, devices, or findings mentioned
- Keep it under 150 words
- Do not use phrases like "this article discusses" - just provide the facts"""

    try:
        response = model.generate_content(prompt)
        summary = response.text.strip()

        # Fallback if response is too long
        if len(summary) > 500:
            summary = summary[:497] + "..."

        return summary

    except Exception as e:
        print(f"  ⚠️  Gemini API error: {e}")
        return None


def load_feed(filename="feed.json"):
    """Load feed.json"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ {filename} not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading {filename}: {e}")
        sys.exit(1)


def save_feed(items, filename="feed.json"):
    """Save feed data to JSON file"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved {len(items)} items to {filename}")


def main():
    # Get API key from environment
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("   Get your API key from: https://makersuite.google.com/app/apikey")
        print("   Then run: export GEMINI_API_KEY='your-api-key'")
        sys.exit(1)

    print("🤖 Starting Gemini-powered haptic summary generation")
    print("=" * 60)

    # Load existing feed
    items = load_feed()
    print(f"📂 Loaded {len(items)} items from feed.json")

    # Check which items need summaries
    items_to_process = [item for item in items if not item.get("ai_summary")]
    items_with_summaries = len(items) - len(items_to_process)

    print(f"✅ {items_with_summaries} items already have summaries")
    print(f"🔄 {len(items_to_process)} items need processing")

    if len(items_to_process) == 0:
        print("✨ All items already have summaries!")
        return

    # Process items
    print()
    for idx, item in enumerate(items_to_process, 1):
        print(f"[{idx}/{len(items_to_process)}] Processing: {item['title'][:60]}...")

        summary = generate_haptic_summary(
            item["title"],
            item.get("description", ""),
            item["link"],
            api_key
        )

        if summary:
            item["ai_summary"] = summary
            print(f"  ✅ Generated summary")
        else:
            item["ai_summary"] = "Unable to generate summary"
            print(f"  ⚠️  Failed to generate summary")

        # Rate limiting - Gemini free tier: 60 requests per minute
        if idx < len(items_to_process):
            time.sleep(1.5)  # ~40 requests per minute to be safe

    # Save updated feed
    print()
    print("=" * 60)
    save_feed(items)
    print("✅ Summary generation complete!")


if __name__ == "__main__":
    main()
