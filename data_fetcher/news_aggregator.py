"""News aggregator for Chinese and international financial news."""
import requests
import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime


class NewsAggregator:
    """Aggregate financial news from multiple sources."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

    def search_news(self, keyword: str, source: str = "all", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search news by keyword across multiple sources.

        Args:
            keyword: Search keyword
            source: "caixin", "wsj", "eastmoney", "bloomberg", "ft", or "all"
            limit: Maximum number of results

        Returns:
            List of news articles.
        """
        results = []
        if source in ["eastmoney", "all"]:
            results.extend(self._get_eastmoney_news(limit))
        if source in ["bloomberg", "all"]:
            results.extend(self._get_bloomberg_news(limit))
        if source in ["ft", "all"]:
            results.extend(self._get_ft_news(limit))
        if source in ["yahoo", "all"]:
            results.extend(self._get_yahoo_news(keyword, limit))
        if source in ["wsj", "all"]:
            results.extend(self._get_wsj_news(keyword, limit))
        if source in ["caixin", "all"]:
            results.extend(self._get_caixin_news(keyword, limit))
        return results[:limit]

    def _get_eastmoney_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get real-time news from EastMoney."""
        try:
            url = "https://newsapi.eastmoney.com/kuaixun/v1/getlist_101_ajaxResult_50_1_.html"
            resp = self.session.get(url, timeout=10)
            text = resp.text.strip()

            match = re.search(r'var ajaxResult=(.+)', text)
            if not match:
                return []

            data = json.loads(match.group(1))
            articles = []
            for item in data.get("LivesList", [])[:limit]:
                articles.append({
                    "source": "eastmoney",
                    "title": item.get("title", ""),
                    "url": item.get("url_w", ""),
                    "time": item.get("showtime", ""),
                    "summary": "",
                })
            return articles
        except Exception as e:
            print(f"Error fetching EastMoney news: {e}")
            return []

    def _get_bloomberg_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get Bloomberg Markets news."""
        try:
            url = "https://feeds.bloomberg.com/markets/news.rss"
            resp = self.session.get(url, timeout=10)
            if resp.status_code != 200:
                return []

            items = re.findall(r'<item>(.*?)</item>', resp.text, re.DOTALL)
            articles = []
            for item in items[:limit]:
                title = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                link = re.search(r'<link>(.*?)</link>', item)
                pubdate = re.search(r'<pubDate>(.*?)</pubDate>', item)
                if title:
                    articles.append({
                        "source": "bloomberg",
                        "title": title.group(1).strip(),
                        "url": link.group(1).strip() if link else "#",
                        "time": pubdate.group(1).strip()[:16] if pubdate else "",
                        "summary": "",
                    })
            return articles
        except Exception as e:
            print(f"Error fetching Bloomberg news: {e}")
            return []

    def _get_ft_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get Financial Times news."""
        try:
            url = "https://www.ft.com/rss/home"
            resp = self.session.get(url, timeout=10)
            if resp.status_code != 200:
                return []

            items = re.findall(r'<item>(.*?)</item>', resp.text, re.DOTALL)
            articles = []
            for item in items[:limit]:
                title = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                link = re.search(r'<link>(.*?)</link>', item)
                pubdate = re.search(r'<pubDate>(.*?)</pubDate>', item)
                if title:
                    articles.append({
                        "source": "ft",
                        "title": title.group(1).strip(),
                        "url": link.group(1).strip() if link else "#",
                        "time": pubdate.group(1).strip()[:16] if pubdate else "",
                        "summary": "",
                    })
            return articles
        except Exception as e:
            print(f"Error fetching FT news: {e}")
            return []

    def _get_yahoo_news(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get finance news from Yahoo Finance."""
        try:
            url = "https://finance.yahoo.com/markets/news/"
            resp = self.session.get(url, timeout=10)

            articles = []
            script_pattern = r'"heading":"([^"]+)","imageUrl"'
            headings = re.findall(script_pattern, resp.text[:500000])[:limit]
            for h in headings:
                articles.append({
                    "source": "yahoo",
                    "title": h[:200],
                    "url": "#",
                    "time": "",
                    "summary": "",
                })
            return articles
        except Exception as e:
            print(f"Error fetching Yahoo news: {e}")
            return []

    def _get_wsj_news(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get WSJ news via CNBC alternative."""
        try:
            # CNBC Tech/Gadgets RSS as WSJ alternative
            url = "https://www.cnbc.com/id/100003114/device/rss/rss.html"
            resp = self.session.get(url, timeout=10)
            if resp.status_code != 200:
                return []

            items = re.findall(r'<item>(.*?)</item>', resp.text, re.DOTALL)
            articles = []
            for item in items[:limit]:
                title = re.search(r'<title>(.*?)</title>', item)
                link = re.search(r'<link>(.*?)</link>', item)
                pubdate = re.search(r'<pubDate>(.*?)</pubDate>', item)
                if title:
                    articles.append({
                        "source": "cnbc",
                        "title": title.group(1).strip(),
                        "url": link.group(1).strip() if link else "#",
                        "time": pubdate.group(1).strip()[:16] if pubdate else "",
                        "summary": "",
                    })
            return articles
        except Exception as e:
            print(f"Error fetching WSJ news: {e}")
            return []

    def _get_caixin_news(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get Caixin news via direct scraping."""
        try:
            url = f"https://www.caixinglobal.com/rss/{keyword if keyword else 'business'}.xml"
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200 and len(resp.text) > 100:
                items = re.findall(r'<item>(.*?)</item>', resp.text, re.DOTALL)
                articles = []
                for item in items[:limit]:
                    title = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                    link = re.search(r'<link>(.*?)</link>', item)
                    pubdate = re.search(r'<pubDate>(.*?)</pubDate>', item)
                    if title:
                        articles.append({
                            "source": "caixin",
                            "title": title.group(1).strip(),
                            "url": link.group(1).strip() if link else "#",
                            "time": pubdate.group(1).strip()[:16] if pubdate else "",
                            "summary": "",
                        })
                return articles
            return []
        except Exception as e:
            print(f"Error fetching Caixin news: {e}")
            return []

    def get_stock_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get news related to a specific stock.
        """
        symbol_map = {
            "0700.HK": "腾讯",
            "9988.HK": "阿里巴巴",
            "600519": "贵州茅台",
            "AAPL": "Apple",
            "NVDA": "Nvidia",
            "TSLA": "Tesla",
            "MSFT": "Microsoft",
            "GOOGL": "Google",
            "AMZN": "Amazon",
            "META": "Meta",
        }
        keyword = symbol_map.get(symbol, symbol)
        return self.search_news(keyword, source="all", limit=limit)
