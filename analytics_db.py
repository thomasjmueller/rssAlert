#!/usr/bin/env python3
"""
Import feed.json into SQLite database for advanced analytics
Usage: python3 analytics_db.py
"""

import json
import sqlite3
from datetime import datetime

def create_database():
    """Create SQLite database with proper schema"""

    conn = sqlite3.connect('analytics.db')
    cursor = conn.cursor()

    # Articles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            link TEXT UNIQUE NOT NULL,
            date TEXT NOT NULL,
            source TEXT,
            description TEXT,
            ai_summary TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Keywords table (many-to-many relationship)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT UNIQUE NOT NULL
        )
    ''')

    # Article-Keyword junction table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS article_keywords (
            article_id INTEGER,
            keyword_id INTEGER,
            FOREIGN KEY (article_id) REFERENCES articles(id),
            FOREIGN KEY (keyword_id) REFERENCES keywords(id),
            PRIMARY KEY (article_id, keyword_id)
        )
    ''')

    # Indexes for faster queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON articles(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON articles(source)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_keyword ON keywords(keyword)')

    conn.commit()
    return conn

def import_feed(conn):
    """Import feed.json into database"""

    cursor = conn.cursor()

    # Load feed
    with open('feed.json', 'r', encoding='utf-8') as f:
        items = json.load(f)

    imported = 0
    skipped = 0

    for item in items:
        # Check if article already exists
        cursor.execute('SELECT id FROM articles WHERE link = ?', (item['link'],))
        existing = cursor.fetchone()

        if existing:
            article_id = existing[0]
            # Update if needed
            cursor.execute('''
                UPDATE articles
                SET ai_summary = ?, description = ?
                WHERE id = ?
            ''', (item.get('ai_summary'), item.get('description'), article_id))
            skipped += 1
        else:
            # Insert new article
            cursor.execute('''
                INSERT INTO articles (title, link, date, source, description, ai_summary)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                item['title'],
                item['link'],
                item['date'],
                item.get('source', 'unknown'),
                item.get('description', ''),
                item.get('ai_summary', '')
            ))
            article_id = cursor.lastrowid
            imported += 1

        # Insert keywords
        keywords = item.get('keywords', [])
        for kw in keywords:
            # Insert keyword if not exists
            cursor.execute('INSERT OR IGNORE INTO keywords (keyword) VALUES (?)', (kw,))
            cursor.execute('SELECT id FROM keywords WHERE keyword = ?', (kw,))
            keyword_id = cursor.fetchone()[0]

            # Link article to keyword
            cursor.execute('''
                INSERT OR IGNORE INTO article_keywords (article_id, keyword_id)
                VALUES (?, ?)
            ''', (article_id, keyword_id))

    conn.commit()
    print(f"✅ Imported {imported} new articles, updated {skipped} existing")
    return imported, skipped

def print_stats(conn):
    """Print database statistics"""

    cursor = conn.cursor()

    # Total articles
    cursor.execute('SELECT COUNT(*) FROM articles')
    total_articles = cursor.fetchone()[0]

    # Total keywords
    cursor.execute('SELECT COUNT(*) FROM keywords')
    total_keywords = cursor.fetchone()[0]

    # Articles with summaries
    cursor.execute('SELECT COUNT(*) FROM articles WHERE ai_summary IS NOT NULL AND ai_summary != ""')
    with_summaries = cursor.fetchone()[0]

    # Date range
    cursor.execute('SELECT MIN(date), MAX(date) FROM articles')
    date_range = cursor.fetchone()

    # Top keywords
    cursor.execute('''
        SELECT k.keyword, COUNT(*) as count
        FROM keywords k
        JOIN article_keywords ak ON k.id = ak.keyword_id
        GROUP BY k.keyword
        ORDER BY count DESC
        LIMIT 10
    ''')
    top_keywords = cursor.fetchall()

    # Top sources
    cursor.execute('''
        SELECT source, COUNT(*) as count
        FROM articles
        GROUP BY source
        ORDER BY count DESC
        LIMIT 10
    ''')
    top_sources = cursor.fetchall()

    print("\n📊 Database Statistics")
    print("=" * 60)
    print(f"Total articles: {total_articles}")
    print(f"Total unique keywords: {total_keywords}")
    print(f"Articles with AI summaries: {with_summaries}")
    print(f"Date range: {date_range[0]} to {date_range[1]}")

    print(f"\n🔥 Top 10 Keywords:")
    for kw, count in top_keywords:
        print(f"  {kw}: {count}")

    print(f"\n📰 Top 10 Sources:")
    for source, count in top_sources:
        print(f"  {source}: {count}")

def main():
    print("🗄️  Creating/updating analytics database...")

    conn = create_database()
    imported, skipped = import_feed(conn)
    print_stats(conn)

    conn.close()

    print("\n✅ Database ready: analytics.db")
    print("Use SQL queries or build analytics scripts on top of this!")

if __name__ == "__main__":
    main()
