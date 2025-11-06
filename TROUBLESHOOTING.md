# Troubleshooting Guide

## Website Shows "Sample RSS Feed Item"

This means the Python script hasn't run successfully yet. Here's how to fix it:

### 1. Check if RSS_FEED_URL Secret is Set

**In GitHub:**
- Go to your repository
- Settings → Secrets and variables → Actions
- Look for `RSS_FEED_URL` in the list
- If not there, click "New repository secret" and add it

**The secret value should be your RSS feed URL**, like:
- `https://example.com/rss`
- `https://example.com/feed.xml`
- `https://blog.example.com/rss.xml`

### 2. Test Locally First

Before running in GitHub Actions, test on your local machine:

```bash
# Set your RSS feed URL
export RSS_FEED_URL="https://your-feed-url.com/rss"

# Install dependencies
pip install -r requirements.txt

# Run the script
python fetch_rss.py

# Check the output
cat feed.json
```

If this works locally, you should see actual feed data in `feed.json` instead of the sample data.

### 3. Run the GitHub Action

Once the secret is set:

1. Go to **Actions** tab
2. Click **"Update RSS Feed"** workflow on the left
3. Click **"Run workflow"** button (top right)
4. Select the `main` branch
5. Click **"Run workflow"**

### 4. Check the Workflow Logs

If the workflow fails:

1. Go to **Actions** tab
2. Click on the failed workflow run
3. Click on the **"update-feed"** job
4. Expand each step to see error messages

**Common errors:**

- ❌ "RSS_FEED_URL secret is not set" → Add the secret (step 1)
- ❌ "Failed to load feed" → Check your RSS URL is valid
- ❌ "Permission denied" → Check workflow permissions

### 5. Verify GitHub Pages is Enabled

1. Go to **Settings** → **Pages**
2. Source should be set to: **"Deploy from a branch"**
3. Branch should be: **main** / **(root)**
4. Click **Save** if you changed anything
5. Wait 2-3 minutes for deployment

### 6. Check feed.json in Repository

After a successful workflow run:

1. Go to your repository files
2. Look for `feed.json` in the root
3. Click on it to view contents
4. It should contain your actual RSS items, not sample data

If `feed.json` has real data but the website still shows sample data, try:
- Hard refresh the page (Ctrl+F5 or Cmd+Shift+R)
- Clear browser cache
- Wait a few minutes for GitHub Pages to redeploy

## Still Having Issues?

### Debug the Python Script

Add debug output to see what's happening:

```bash
# Run with verbose output
export RSS_FEED_URL="https://your-feed-url.com/rss"
python -u fetch_rss.py

# Check if the URL is accessible
curl -I "https://your-feed-url.com/rss"
```

### Common RSS Feed Issues

- **404 Error**: RSS feed URL is wrong
- **SSL Error**: Try using `http://` instead of `https://` (not recommended)
- **Empty Feed**: Feed might be empty or malformed
- **Rate Limiting**: Some feeds block automated requests

### Workflow Permissions

Make sure the workflow has write permissions:

1. Settings → Actions → General
2. Scroll to "Workflow permissions"
3. Select "Read and write permissions"
4. Click Save

## Quick Test Checklist

- [ ] RSS_FEED_URL secret is set in GitHub
- [ ] Secret value is a valid RSS feed URL
- [ ] Python script runs successfully locally
- [ ] Workflow completes without errors
- [ ] feed.json exists and contains real data
- [ ] GitHub Pages is enabled and deployed
- [ ] Browser cache is cleared

## Need More Help?

Check the error messages in:
1. GitHub Actions logs (Actions tab)
2. Browser console (F12 → Console tab)
3. GitHub Pages deployment logs (Actions tab → pages-build-deployment)
