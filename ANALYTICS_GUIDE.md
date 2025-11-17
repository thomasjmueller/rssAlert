# Analytics Guide

Your haptics RSS feed now has powerful analytics capabilities!

## Quick Start

### 1. Import to Database

```bash
# After processing all summaries, create analytics database
python3 analytics_db.py
```

This creates `analytics.db` with:
- Articles table (title, link, date, source, summary)
- Keywords table (all unique keywords)
- Relationships between articles and keywords

### 2. Run Analytics

```bash
python3 analytics_examples.py
```

Shows:
- 📈 Keyword trends (last 30 days)
- 🎮 Device popularity (iPhone vs DualSense vs Quest, etc.)
- 📅 Article volume per week
- 📊 Content categories (research vs commercial vs gaming)
- 🔥 Hot topics this week (vs last week)
- 🌟 Emerging keywords (new or surging topics)

## Available Analytics

### 1. Keyword Trends Over Time
See which topics are growing or declining:
- VR haptics trending up
- Mobile haptics steady
- Gaming controllers peaking

### 2. Device Analysis
Track mentions of specific devices:
- DualSense vs Xbox controller
- iPhone vs Android haptics
- Quest 3 adoption rate

### 3. Source Quality
Identify best sources:
- Which sources provide deepest coverage?
- Reddit vs YouTube vs Research papers
- Most consistent publishers

### 4. Temporal Patterns
Discover publishing patterns:
- Weekly article volume
- Best days for new content
- Seasonal trends

### 5. Topic Clustering
Group related content:
- VR/AR haptics
- Mobile device haptics
- Gaming controllers
- Research/Academic
- Product reviews

### 6. Emerging Topics
Catch new trends early:
- New devices launching
- New research areas
- Shifting industry focus

## Custom Queries

Use SQL directly for custom analysis:

```python
import sqlite3

conn = sqlite3.connect('analytics.db')
cursor = conn.cursor()

# Example: Find all articles about a specific device
cursor.execute('''
    SELECT a.title, a.date, a.link
    FROM articles a
    JOIN article_keywords ak ON a.id = ak.article_id
    JOIN keywords k ON ak.keyword_id = k.id
    WHERE k.keyword = 'dualsense'
    ORDER BY a.date DESC
''')

for title, date, link in cursor.fetchall():
    print(f"{date}: {title}")

conn.close()
```

## Advanced Analytics (Future)

### Web Dashboard
Create `analytics.html` with interactive charts:
- Chart.js for line/bar charts
- D3.js for network graphs
- Plotly for advanced visualizations

### Export Reports
```bash
# Generate weekly report
python3 generate_report.py --period week --format pdf

# Export to CSV for Excel analysis
python3 export_analytics.py --format csv
```

### API Integration
Query your data via REST API:
```bash
GET /api/trends?period=30days
GET /api/keywords/dualsense
GET /api/sources/reddit
```

## Database Schema

```sql
-- Articles
articles (id, title, link, date, source, description, ai_summary)

-- Keywords
keywords (id, keyword)

-- Relationships
article_keywords (article_id, keyword_id)
```

## Analysis Examples

### Find Most Discussed Devices (Last Month)

```sql
SELECT k.keyword, COUNT(*) as mentions
FROM articles a
JOIN article_keywords ak ON a.id = ak.article_id
JOIN keywords k ON ak.keyword_id = k.id
WHERE a.date >= datetime('now', '-30 days')
  AND k.keyword IN ('iphone', 'dualsense', 'quest', 'ps5', 'xbox')
GROUP BY k.keyword
ORDER BY mentions DESC;
```

### Compare Research vs Commercial Content

```sql
-- Research articles
SELECT COUNT(*) FROM articles
WHERE ai_summary LIKE '%research%'
   OR ai_summary LIKE '%study%'
   OR ai_summary LIKE '%paper%';

-- Product reviews
SELECT COUNT(*) FROM articles
WHERE ai_summary LIKE '%review%'
   OR ai_summary LIKE '%test%'
   OR ai_summary LIKE '%unboxing%';
```

### Keyword Co-occurrence (What topics appear together?)

```sql
SELECT
    k1.keyword as keyword1,
    k2.keyword as keyword2,
    COUNT(*) as co_occurrences
FROM article_keywords ak1
JOIN article_keywords ak2 ON ak1.article_id = ak2.article_id
JOIN keywords k1 ON ak1.keyword_id = k1.id
JOIN keywords k2 ON ak2.keyword_id = k2.id
WHERE k1.keyword < k2.keyword  -- Avoid duplicates
GROUP BY k1.keyword, k2.keyword
HAVING co_occurrences >= 3
ORDER BY co_occurrences DESC
LIMIT 20;
```

This shows patterns like:
- "dualsense" + "ps5" (always together)
- "vr" + "quest" (common pair)
- "gaming" + "controller" (related topics)

### Source Productivity Over Time

```sql
SELECT
    source,
    strftime('%Y-%m', date) as month,
    COUNT(*) as articles
FROM articles
GROUP BY source, month
ORDER BY month DESC, articles DESC;
```

### Average Keywords Per Article by Source

```sql
SELECT
    a.source,
    AVG(keyword_count) as avg_keywords
FROM articles a
JOIN (
    SELECT article_id, COUNT(*) as keyword_count
    FROM article_keywords
    GROUP BY article_id
) kc ON a.id = kc.article_id
GROUP BY a.source
ORDER BY avg_keywords DESC;
```

Shows which sources provide richest content.

## Visualization Ideas

### 1. Timeline Heatmap
GitHub-style contribution graph showing article activity

### 2. Keyword Cloud
Size = frequency, Color = trend (growing/declining)

### 3. Network Graph
Nodes = keywords, Edges = co-occurrence strength

### 4. Sankey Diagram
Flow from sources → topics → devices

### 5. Comparison Charts
Device mentions over time (line chart with multiple series)

## Integration with Existing Site

Add analytics section to `index.html`:

```html
<!-- Analytics Link -->
<a href="analytics.html" class="text-gray-600 hover:text-gray-800">
  📊 View Analytics
</a>
```

## Maintaining the Database

### Update Database (Run After New Articles)

```bash
# Fetch new RSS items
python3 fetch_rss.py

# Process summaries
python3 process_all.py

# Update database
python3 analytics_db.py
```

### Backup Database

```bash
# SQLite backup
sqlite3 analytics.db ".backup analytics_backup.db"

# Or simple copy
cp analytics.db analytics.db.backup
```

## Cost & Performance

- SQLite file size: ~1-2MB for 1000 articles
- Query speed: <10ms for most queries
- No hosting costs (runs locally)
- Can handle 100K+ articles easily

## Why SQLite + JSON?

**JSON (`feed.json`):**
- ✅ Powers GitHub Pages website
- ✅ Version controlled
- ✅ Easy to read/edit
- ✅ Perfect for static site

**SQLite (`analytics.db`):**
- ✅ Fast complex queries
- ✅ Aggregations and analytics
- ✅ No server needed
- ✅ Portable single file

Best of both worlds!

## Next Steps

1. **Run initial analytics**: `python3 analytics_db.py && python3 analytics_examples.py`
2. **Create custom queries** for your research questions
3. **Build visualizations** (optional, but powerful)
4. **Schedule updates** (add to GitHub Actions)
5. **Export reports** for sharing with colleagues

---

Questions or ideas? Check the example scripts for inspiration!
