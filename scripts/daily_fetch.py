#!/usr/bin/env python3
"""Daily market data fetcher - runs at 9:00 AM every day."""
import sys
sys.path.insert(0, '/home/jiguo/workspace/stock-trading-assistant')

import json
import sqlite3
from datetime import datetime, date
from pathlib import Path

from data_fetcher.yahoo_finance import YahooFinanceFetcher
from data_fetcher.eastmoney import EastMoneyFetcher
from data_fetcher.news_aggregator import NewsAggregator
from analyzer.market_trend import MarketTrendAnalyzer


DB_PATH = Path("/home/jiguo/workspace/stock-trading-assistant/data/daily_cache.db")
DB_PATH.parent.mkdir(exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS market_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            market TEXT NOT NULL,
            data TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS news_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            data TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def save_market_snapshot(conn, market: str, analysis: dict):
    conn.execute(
        "INSERT INTO market_snapshots (date, market, data, created_at) VALUES (?, ?, ?, ?)",
        (date.today().isoformat(), market, json.dumps(analysis, ensure_ascii=False), datetime.now().isoformat())
    )
    conn.commit()


def save_news_snapshot(conn, news: list):
    conn.execute(
        "INSERT INTO news_cache (date, data, created_at) VALUES (?, ?, ?)",
        (date.today().isoformat(), json.dumps(news, ensure_ascii=False), datetime.now().isoformat())
    )
    conn.commit()


def main():
    print(f"[{datetime.now().isoformat()}] Starting daily market data fetch...")

    conn = init_db()
    analyzer = MarketTrendAnalyzer()

    # Fetch A-share
    print("  Fetching A-share market...")
    a_share = analyzer.analyze_market("a")
    save_market_snapshot(conn, "a-share", a_share)
    print(f"    A-share: {a_share.get('trend', 'unknown')} ({a_share.get('avg_change_percent', 0):+.2f}%)")

    # Fetch HK market
    print("  Fetching HK market...")
    hk = analyzer.analyze_market("hk")
    save_market_snapshot(conn, "hk", hk)
    print(f"    HK: {hk.get('trend', 'unknown')} ({hk.get('avg_change_percent', 0):+.2f}%)")

    # Fetch US market
    print("  Fetching US market...")
    us = analyzer.analyze_market("us")
    save_market_snapshot(conn, "us", us)
    print(f"    US: {us.get('trend', 'unknown')} ({us.get('avg_change_percent', 0):+.2f}%)")

    # Fetch news
    print("  Fetching news...")
    news = analyzer.get_market_news("all", limit=20)
    save_news_snapshot(conn, news)
    print(f"    Fetched {len(news)} news items")

    conn.close()
    print(f"[{datetime.now().isoformat()}] Daily fetch complete.")


if __name__ == "__main__":
    main()
