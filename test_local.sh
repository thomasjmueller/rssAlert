#!/bin/bash
set -e  # Exit on any error

# Test script to run locally before pushing to GitHub

# Check if RSS_FEED_URL is set
if [ -z "$RSS_FEED_URL" ]; then
    echo "❌ ERROR: RSS_FEED_URL is not set!"
    echo "Please run: export RSS_FEED_URL=\"https://your-feed-url.com/rss\""
    exit 1
fi

echo "📡 RSS Feed URL: $RSS_FEED_URL"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
elif command -v pip &> /dev/null; then
    pip install -r requirements.txt
else
    echo "❌ ERROR: pip or pip3 not found. Please install Python first."
    exit 1
fi

echo ""

# Run the script
echo "🔄 Fetching RSS feed..."
if command -v python3 &> /dev/null; then
    python3 fetch_rss.py
elif command -v python &> /dev/null; then
    python fetch_rss.py
else
    echo "❌ ERROR: python or python3 not found."
    exit 1
fi

echo ""

# Check if feed.json was created/updated and has real data
if [ -f "feed.json" ]; then
    ITEM_COUNT=$(grep -o '"title"' feed.json | wc -l | tr -d ' ')

    if [ "$ITEM_COUNT" -gt 0 ]; then
        echo "✅ Success! feed.json has been created/updated"
        echo "📊 Number of items: $ITEM_COUNT"
        echo ""
        echo "Preview of first item:"
        head -20 feed.json
    else
        echo "⚠️  feed.json exists but appears to be empty"
    fi
else
    echo "❌ Error: feed.json was not created"
    exit 1
fi
