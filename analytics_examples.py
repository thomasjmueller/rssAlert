#!/usr/bin/env python3
"""
Example analytics queries on the SQLite database
Usage: python3 analytics_examples.py
"""

import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta

def connect_db():
    """Connect to analytics database"""
    return sqlite3.connect('analytics.db')

def keyword_trends_last_30_days():
    """Show keyword trends over last 30 days"""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            k.keyword,
            DATE(a.date) as day,
            COUNT(*) as count
        FROM articles a
        JOIN article_keywords ak ON a.id = ak.article_id
        JOIN keywords k ON ak.keyword_id = k.id
        WHERE a.date >= datetime('now', '-30 days')
        GROUP BY k.keyword, DATE(a.date)
        ORDER BY k.keyword, day
    ''')

    trends = defaultdict(list)
    for keyword, day, count in cursor.fetchall():
        trends[keyword].append((day, count))

    print("📈 Keyword Trends (Last 30 Days)")
    print("=" * 60)
    for keyword, data in sorted(trends.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        total = sum(c for _, c in data)
        print(f"{keyword}: {total} mentions across {len(data)} days")

    conn.close()

def device_popularity():
    """Compare device popularity"""
    conn = connect_db()
    cursor = conn.cursor()

    # Common device keywords
    devices = ['iphone', 'dualsense', 'quest', 'ps5', 'xbox', 'apple watch',
               'steam deck', 'switch', 'oneplus', 'pixel']

    print("\n🎮 Device Popularity")
    print("=" * 60)

    for device in devices:
        cursor.execute('''
            SELECT COUNT(DISTINCT a.id)
            FROM articles a
            JOIN article_keywords ak ON a.id = ak.article_id
            JOIN keywords k ON ak.keyword_id = k.id
            WHERE k.keyword LIKE ?
        ''', (f'%{device}%',))

        count = cursor.fetchone()[0]
        if count > 0:
            print(f"{device.title()}: {count} articles")

    conn.close()

def articles_per_week():
    """Show article volume per week"""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            strftime('%Y-W%W', date) as week,
            COUNT(*) as count
        FROM articles
        GROUP BY week
        ORDER BY week DESC
        LIMIT 12
    ''')

    print("\n📅 Article Volume (Last 12 Weeks)")
    print("=" * 60)
    for week, count in cursor.fetchall():
        bar = '█' * (count // 2)
        print(f"{week}: {bar} {count}")

    conn.close()

def research_vs_commercial():
    """Analyze research vs commercial content"""
    conn = connect_db()
    cursor = conn.cursor()

    # Research indicators
    cursor.execute('''
        SELECT COUNT(DISTINCT a.id)
        FROM articles a
        JOIN article_keywords ak ON a.id = ak.article_id
        JOIN keywords k ON ak.keyword_id = k.id
        WHERE k.keyword IN ('research', 'study', 'paper', 'academic', 'university')
    ''')
    research_count = cursor.fetchone()[0]

    # Commercial indicators
    cursor.execute('''
        SELECT COUNT(DISTINCT a.id)
        FROM articles a
        JOIN article_keywords ak ON a.id = ak.article_id
        JOIN keywords k ON ak.keyword_id = k.id
        WHERE k.keyword IN ('review', 'product', 'release', 'launch', 'buy')
    ''')
    commercial_count = cursor.fetchone()[0]

    # Gaming
    cursor.execute('''
        SELECT COUNT(DISTINCT a.id)
        FROM articles a
        JOIN article_keywords ak ON a.id = ak.article_id
        JOIN keywords k ON ak.keyword_id = k.id
        WHERE k.keyword IN ('gaming', 'game', 'controller', 'console')
    ''')
    gaming_count = cursor.fetchone()[0]

    print("\n📊 Content Categories")
    print("=" * 60)
    print(f"Research/Academic: {research_count} articles")
    print(f"Commercial/Reviews: {commercial_count} articles")
    print(f"Gaming: {gaming_count} articles")

    conn.close()

def hot_topics_this_week():
    """Identify trending topics this week vs last week"""
    conn = connect_db()
    cursor = conn.cursor()

    # This week
    cursor.execute('''
        SELECT k.keyword, COUNT(*) as count
        FROM articles a
        JOIN article_keywords ak ON a.id = ak.article_id
        JOIN keywords k ON ak.keyword_id = k.id
        WHERE a.date >= datetime('now', '-7 days')
        GROUP BY k.keyword
        ORDER BY count DESC
        LIMIT 10
    ''')
    this_week = dict(cursor.fetchall())

    # Last week
    cursor.execute('''
        SELECT k.keyword, COUNT(*) as count
        FROM articles a
        JOIN article_keywords ak ON a.id = ak.article_id
        JOIN keywords k ON ak.keyword_id = k.id
        WHERE a.date >= datetime('now', '-14 days')
        AND a.date < datetime('now', '-7 days')
        GROUP BY k.keyword
    ''')
    last_week = dict(cursor.fetchall())

    print("\n🔥 Hot Topics This Week")
    print("=" * 60)
    for keyword, count in sorted(this_week.items(), key=lambda x: x[1], reverse=True):
        last_count = last_week.get(keyword, 0)
        change = count - last_count
        trend = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        print(f"{trend} {keyword}: {count} articles (Δ {change:+d})")

    conn.close()

def emerging_keywords():
    """Find keywords that appeared recently but weren't common before"""
    conn = connect_db()
    cursor = conn.cursor()

    # Keywords in last 7 days
    cursor.execute('''
        SELECT k.keyword, COUNT(*) as recent_count
        FROM articles a
        JOIN article_keywords ak ON a.id = ak.article_id
        JOIN keywords k ON ak.keyword_id = k.id
        WHERE a.date >= datetime('now', '-7 days')
        GROUP BY k.keyword
        HAVING recent_count >= 2
    ''')
    recent_keywords = dict(cursor.fetchall())

    # Historical count for these keywords
    emerging = []
    for keyword, recent_count in recent_keywords.items():
        cursor.execute('''
            SELECT COUNT(*) as historical_count
            FROM articles a
            JOIN article_keywords ak ON a.id = ak.article_id
            JOIN keywords k ON ak.keyword_id = k.id
            WHERE k.keyword = ?
            AND a.date < datetime('now', '-7 days')
        ''', (keyword,))

        historical_count = cursor.fetchone()[0]

        # Emerging if recent activity is significantly higher than historical
        if historical_count == 0 or recent_count > historical_count * 2:
            emerging.append((keyword, recent_count, historical_count))

    print("\n🌟 Emerging Keywords (New or Surging)")
    print("=" * 60)
    for keyword, recent, historical in sorted(emerging, key=lambda x: x[1], reverse=True)[:10]:
        print(f"{keyword}: {recent} recent vs {historical} historical")

    conn.close()

def main():
    try:
        keyword_trends_last_30_days()
        device_popularity()
        articles_per_week()
        research_vs_commercial()
        hot_topics_this_week()
        emerging_keywords()
    except sqlite3.OperationalError:
        print("❌ Database not found. Run: python3 analytics_db.py first")

if __name__ == "__main__":
    main()
