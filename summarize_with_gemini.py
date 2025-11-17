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


def generate_haptic_summary_and_keywords(title, description, url, api_key, existing_keywords=None, max_retries=3):
    """Generate a haptic-focused summary and extract keywords using Gemini API"""

    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-flash-latest')

    # Fetch article content for better context
    article_content = fetch_article_content(url)

    # Build prompt
    prompt = f"""Analyze this article and provide:
1. A concise summary (2-3 sentences) focused ONLY on haptic/tactile feedback content
2. Up to 4 keywords

Title: {title}
Description: {description}

"""

    if article_content:
        prompt += f"Article Content (excerpt): {article_content[:3000]}\n\n"

    prompt += """Summary Instructions:
- Focus exclusively on haptic, tactile, or touch feedback related content
- Be specific about haptic technologies, techniques, devices, or findings mentioned
- Keep it under 150 words
- Do not use phrases like "this article discusses" or "the text introduces" - just provide the facts in a highly concise manner

Keyword Instructions:
- Extract up to 4 keywords (device names, software names, person names, or abstract words like: review, gaming, test, design, prototyping, research, accessibility, VR, AR, wearable, etc.)
- Keep keywords short (1-2 words max)
- Use lowercase
- DO NOT use generic haptic terms: haptic, haptics, vibration, vibrations, tactile
"""

    if existing_keywords:
        prompt += f"\nPreferred keywords (REUSE these when applicable): {', '.join(sorted(existing_keywords))}\n"

    prompt += """\nOutput format (use exactly this format):
SUMMARY: [your summary here]
KEYWORDS: keyword1, keyword2, keyword3, keyword4"""

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            result = response.text.strip()

            # Parse the response
            summary = ""
            keywords = []

            # Excluded keywords (too generic for haptics research)
            excluded_keywords = {'haptic', 'haptics', 'vibration', 'vibrations', 'tactile'}

            lines = result.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('SUMMARY:'):
                    summary = line.replace('SUMMARY:', '').strip()
                elif line.startswith('KEYWORDS:'):
                    keywords_str = line.replace('KEYWORDS:', '').strip()
                    keywords = [
                        k.strip().lower()
                        for k in keywords_str.split(',')
                        if k.strip() and k.strip().lower() not in excluded_keywords
                    ]
                    keywords = keywords[:4]  # Max 4 keywords

            # Fallback if parsing fails
            if not summary:
                summary = result[:500] if len(result) <= 500 else result[:497] + "..."

            return summary, keywords

        except Exception as e:
            error_msg = str(e)

            # Check if it's a rate limit error
            if "429" in error_msg or "quota" in error_msg.lower():
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 10  # 10s, 20s, 40s
                    print(f"  ⏳ Rate limit hit, waiting {wait_time}s before retry {attempt + 2}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"  ⚠️  Rate limit exceeded after {max_retries} attempts")
                    return None, []
            else:
                print(f"  ⚠️  Gemini API error: {e}")
                return None, []

    return None, []


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

    # Collect existing keywords for reuse
    existing_keywords = set()
    for item in items:
        if item.get("keywords"):
            existing_keywords.update(item["keywords"])

    if existing_keywords:
        print(f"📋 Found {len(existing_keywords)} existing keywords to reuse")

    # Check which items need summaries
    items_to_process = [item for item in items if not item.get("ai_summary")]
    items_with_summaries = len(items) - len(items_to_process)

    print(f"✅ {items_with_summaries} items already have summaries")
    print(f"🔄 {len(items_to_process)} items need processing")

    if len(items_to_process) == 0:
        print("✨ All items already have summaries!")
        return

    # Batch processing to respect rate limits
    batch_size = int(os.environ.get("BATCH_SIZE", "10"))
    if len(items_to_process) > batch_size:
        print(f"⚠️  Processing only {batch_size} items this run (set BATCH_SIZE to change)")
        items_to_process = items_to_process[:batch_size]

    # Process items
    print()
    processed_count = 0
    for idx, item in enumerate(items_to_process, 1):
        print(f"[{idx}/{len(items_to_process)}] Processing: {item['title'][:60]}...")

        summary, keywords = generate_haptic_summary_and_keywords(
            item["title"],
            item.get("description", ""),
            item["link"],
            api_key,
            existing_keywords
        )

        if summary:
            item["ai_summary"] = summary
            item["keywords"] = keywords
            print(f"  ✅ Generated summary + keywords: {', '.join(keywords) if keywords else 'none'}")

            # Add new keywords to existing set
            existing_keywords.update(keywords)
            processed_count += 1
        else:
            item["ai_summary"] = "Unable to generate summary"
            item["keywords"] = []
            print(f"  ⚠️  Failed to generate summary")

        # Save progress every 5 items
        if idx % 5 == 0:
            save_feed(items)
            print(f"  💾 Progress saved ({idx} items processed)")

        # Rate limiting - Gemini free tier: 10 requests per minute
        if idx < len(items_to_process):
            print(f"  ⏳ Waiting 7 seconds (rate limit: 10/min)...")
            time.sleep(7)  # ~8-9 requests per minute to be safe

    # Save updated feed
    print()
    print("=" * 60)
    save_feed(items)
    print(f"✅ Summary generation complete! Processed {processed_count} items successfully.")


if __name__ == "__main__":
    main()
