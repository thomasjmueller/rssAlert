# RSS Archive with GitHub Pages

A minimal, searchable RSS feed archive automatically updated via GitHub Actions and hosted on GitHub Pages.

## Features

- 📡 Automatic RSS feed fetching
- 🔍 Real-time search by title or source
- 📅 Sortable by date
- 🎨 Clean, minimal design with Tailwind CSS
- 🌙 Dark mode friendly
- 📱 Fully responsive
- ⚡ No frameworks needed (vanilla JS)
- 🔄 Auto-updates weekly via GitHub Actions

## Setup Instructions

### 1. Create a New GitHub Repository

1. Create a new repository on GitHub (e.g., `rss-archive`)
2. Clone it to your local machine:
   ```bash
   git clone https://github.com/YOUR-USERNAME/rss-archive.git
   cd rss-archive
   ```

### 2. Add the Files

Copy all files from this project to your repository:

```
rss-archive/
├── .github/
│   └── workflows/
│       └── update-feed.yml
├── fetch_rss.py
├── requirements.txt
├── index.html
└── README.md
```

### 3. Configure Your RSS Feed URL

You have two options:

**Option A: Use GitHub Secrets (Recommended)**

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `RSS_FEED_URL`
5. Value: Your RSS feed URL (e.g., `https://example.com/feed.xml`)
6. Click "Add secret"

**Option B: Edit the Python Script Directly**

Edit `fetch_rss.py` line 84:
```python
RSS_FEED_URL = os.environ.get("RSS_FEED_URL", "https://your-feed-url.com/rss")
```

### 4. Enable GitHub Actions

1. Go to your repository on GitHub
2. Navigate to Actions tab
3. If prompted, enable Actions for your repository

### 5. Enable GitHub Pages

1. Go to Settings → Pages
2. Under "Source", select "Deploy from a branch"
3. Under "Branch", select `main` and `/ (root)`
4. Click "Save"
5. Wait a few minutes for deployment

Your site will be available at: `https://YOUR-USERNAME.github.io/rss-archive/`

### 6. Initial Run

For the first run, you'll need to generate the initial `feed.json`:

**Option 1: Run locally**
```bash
# Install dependencies
pip install -r requirements.txt

# Set your RSS feed URL
export RSS_FEED_URL="https://your-feed-url.com/rss"

# Run the script
python fetch_rss.py

# Commit and push
git add feed.json
git commit -m "Initial RSS feed data"
git push
```

**Option 2: Trigger GitHub Action manually**
1. Go to Actions tab
2. Click "Update RSS Feed" workflow
3. Click "Run workflow"
4. Select branch `main` and click "Run workflow"

### 7. Verify It Works

1. Visit your GitHub Pages URL
2. You should see your RSS feed items displayed
3. Test the search functionality
4. Try sorting by clicking the "Date" column header

## Customization

### Change Update Schedule

Edit `.github/workflows/update-feed.yml`:

```yaml
schedule:
  - cron: '0 9 * * 0'  # Every Sunday at 9 AM UTC
```

Cron format: `minute hour day month weekday`

Examples:
- Daily at midnight: `0 0 * * *`
- Every Monday at 8 AM: `0 8 * * 1`
- Twice a week (Mon & Thu at 10 AM): `0 10 * * 1,4`

### Customize the HTML

Edit `index.html` to:
- Change the title and header
- Modify colors (Tailwind classes)
- Add your GitHub repo link in the footer
- Adjust table columns

### Add More Feed Sources

To support multiple RSS feeds, modify `fetch_rss.py` to loop through multiple URLs:

```python
RSS_FEEDS = [
    "https://feed1.com/rss",
    "https://feed2.com/rss",
]

for feed_url in RSS_FEEDS:
    new_items.extend(fetch_rss(feed_url))
```

## Troubleshooting

### GitHub Actions is not running

- Check if Actions are enabled in Settings → Actions
- Verify the `RSS_FEED_URL` secret is set correctly
- Check the Actions tab for error logs

### No data showing on the page

- Make sure `feed.json` exists in the repository
- Run the workflow manually to generate initial data
- Check browser console for errors

### GitHub Pages not deploying

- Ensure Pages is enabled in Settings → Pages
- Wait a few minutes after pushing changes
- Check Actions tab for Pages deployment status

## Local Development

To test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set your RSS feed URL
export RSS_FEED_URL="https://your-feed-url.com/rss"

# Fetch feed
python fetch_rss.py

# Serve locally with Python
python -m http.server 8000

# Open http://localhost:8000 in your browser
```

## Requirements

- Python 3.7+
- feedparser
- requests
- GitHub account
- GitHub Pages enabled repository

## License

MIT License - feel free to use and modify as needed.
