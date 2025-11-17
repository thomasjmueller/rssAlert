# Gemini AI Summary Setup

This guide explains how to set up Gemini API for automatic haptic-focused summaries.

## Features

- **AI-Powered Summaries**: Uses Google's Gemini AI to analyze articles
- **Haptic Focus**: Summaries specifically extract haptic/tactile feedback information
- **Smart Keyword Extraction**: Automatically extracts up to 4 relevant keywords (devices, software, people, abstract concepts)
- **Keyword Reuse**: System learns and reuses existing keywords for consistency
- **Smart Processing**: Fetches full article content for better context
- **Incremental Updates**: Only processes new items without summaries
- **Rate Limited**: Respects Gemini API free tier limits (~8 requests/minute)

## Setup Instructions

### 1. Get Your Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

**Gemini API Free Tier:**
- 10 requests per minute (strictly enforced)
- 1,500 requests per day
- No credit card required
- Script processes ~8 requests/min to stay within limits

### 2. Add API Key to GitHub Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings → Secrets and variables → Actions**
3. Click "New repository secret"
4. Name: `GEMINI_API_KEY`
5. Value: Paste your API key
6. Click "Add secret"

### 3. Test Locally (Optional)

```bash
# Install dependencies
pip install -r requirements.txt

# Set your Gemini API key
export GEMINI_API_KEY="your-api-key-here"

# Run the summarizer (requires feed.json to exist)
python summarize_with_gemini.py

# Process only 5 items (useful for testing)
export BATCH_SIZE=5
python summarize_with_gemini.py
```

**Note:** The script processes 10 items per run by default due to rate limits. Run multiple times to process all items.

### 4. How It Works

The workflow now has these steps:
1. Fetch RSS feed → `feed.json`
2. Generate AI summaries for new items
3. Update `feed.json` with `ai_summary` field
4. Commit and push changes

### 5. Verify Summaries

After the workflow runs:
1. Check `feed.json` - items should have an `ai_summary` field
2. Visit your GitHub Pages site
3. Summaries appear in blue boxes labeled "🤖 HAPTIC SUMMARY"

## Example Output

```json
{
  "title": "New iPhone Haptic Engine Breakthrough",
  "link": "https://example.com/article",
  "date": "2025-11-17T10:00:00",
  "source": "example",
  "description": "Apple announces new haptic technology...",
  "ai_summary": "Apple's new Taptic Engine 2.0 features 50% faster response time (8ms) and supports 16 distinct haptic patterns. The system uses dual linear actuators for directional feedback. Testing shows improved user perception accuracy from 72% to 89%.",
  "keywords": ["iphone", "taptic engine", "actuators", "review"]
}
```

Keywords appear as gray pills below the date on the webpage and are searchable.

## Customizing the Prompt

To modify what the AI focuses on, edit the prompt in `summarize_with_gemini.py` (around line 48-77):

```python
prompt = f"""Your custom prompt here...
Summary Instructions:
- Focus on specific aspects
- Change summary length
- Adjust tone

Keyword Instructions:
- Modify keyword types (add industries, technologies, etc.)
- Change keyword count (currently max 4)
- Adjust keyword style
"""
```

### Keyword Categories

The system extracts these types of keywords:
- **Device names**: iPhone, Quest 3, DualSense, etc.
- **Software/Frameworks**: Unity, Unreal Engine, WebVR, etc.
- **Person names**: Researchers, designers, company leaders
- **Abstract concepts**: gaming, accessibility, prototyping, research, VR, wearable, etc.

Keywords are automatically normalized to lowercase and limited to 1-2 words for consistency.

## Cost Considerations

**Free Tier** (recommended for personal use):
- 1,500 requests/day
- Enough for ~50 articles per day
- No cost

**Paid Tier** (for high-volume):
- $0.00025 per 1K characters input
- $0.0005 per 1K characters output
- ~$0.001-0.01 per article depending on length

## Troubleshooting

### Summaries Not Generated

Check GitHub Actions logs:
```
Actions → Update RSS Feed → Latest run → Generate AI summaries
```

Common issues:
- `GEMINI_API_KEY` not set in secrets
- API rate limit exceeded
- Article URLs blocked or inaccessible

### Low Quality Summaries

The script fetches the first 10KB of each article. For paywalled content:
- Summaries rely on the RSS description
- May be less detailed
- Consider adding custom content extraction

### Rate Limiting

**Free tier has strict limits:**
- 10 requests per minute (hard limit)
- Script waits 7 seconds between requests (~8/min)
- Processes 10 items per run by default
- Automatic retry with exponential backoff on 429 errors

**To process more items:**
```bash
# Increase batch size (use with caution)
export BATCH_SIZE=20
python summarize_with_gemini.py

# Or run multiple times - script only processes items without summaries
python summarize_with_gemini.py
# Wait 1-2 minutes
python summarize_with_gemini.py
```

**For large feeds (100+ items):**
- Let GitHub Actions run weekly - it will gradually process all items
- Or manually run multiple times with breaks

## Disabling AI Summaries

To temporarily disable without removing the code:

**Option 1**: Remove the secret
- Go to Settings → Secrets → Actions
- Delete `GEMINI_API_KEY`
- Workflow will skip summarization

**Option 2**: Comment out workflow step
Edit `.github/workflows/update-feed.yml`:
```yaml
# - name: Generate AI summaries with Gemini
#   env:
#     GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
#   run: |
#     python summarize_with_gemini.py
```

## Advanced: Batch Processing Existing Items

To regenerate all summaries (clears existing ones):

```bash
# Backup first
cp feed.json feed.json.backup

# Clear existing summaries
python -c "import json; data=json.load(open('feed.json')); [item.pop('ai_summary', None) for item in data]; json.dump(data, open('feed.json', 'w'), indent=2)"

# Regenerate all
export GEMINI_API_KEY="your-key"
python summarize_with_gemini.py
```

## Analyzing Keywords

Keywords are stored in `feed.json` and can be extracted for analysis:

### Get All Unique Keywords

```bash
# Extract all unique keywords with counts
python -c "
import json
from collections import Counter

with open('feed.json') as f:
    items = json.load(f)

keywords = []
for item in items:
    keywords.extend(item.get('keywords', []))

counts = Counter(keywords)
print('\nKeyword Frequency:')
for keyword, count in counts.most_common(20):
    print(f'{keyword}: {count}')
"
```

### Export Keywords to CSV

```bash
python -c "
import json
import csv

with open('feed.json') as f:
    items = json.load(f)

with open('keywords_export.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Title', 'Date', 'Keywords', 'Source'])

    for item in items:
        keywords = ', '.join(item.get('keywords', []))
        writer.writerow([item['title'], item['date'], keywords, item['source']])

print('Exported to keywords_export.csv')
"
```

### Use Cases for Keywords

- **Trend Analysis**: Track which devices/concepts are most mentioned over time
- **Content Filtering**: Use search to find all articles about specific devices or concepts
- **Topic Clustering**: Group similar articles by shared keywords
- **Research Planning**: Identify gaps in coverage by analyzing keyword distribution

## Support

- **Gemini API Docs**: https://ai.google.dev/docs
- **API Key Management**: https://makersuite.google.com/app/apikey
- **Rate Limits**: https://ai.google.dev/pricing
