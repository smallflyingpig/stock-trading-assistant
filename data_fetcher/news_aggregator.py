"""News aggregator for Chinese and international financial news."""
import requests
import re
import json
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

TIMEOUT = 5  # 5 second timeout for all external requests


class NewsAggregator:
    """Aggregate financial news from multiple sources."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def search_news(self, keyword: str, source: str = "all", limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch news from all sources in parallel."""
        sources = []

        if source in ["eastmoney", "all"]:
            sources.append(("eastmoney", lambda: self._get_eastmoney_news(limit)))
        if source in ["bloomberg", "all"]:
            sources.append(("bloomberg", lambda: self._get_bloomberg_news(limit)))
        if source in ["ft", "all"]:
            sources.append(("ft", lambda: self._get_ft_news(limit)))
        if source in ["yahoo", "all"]:
            sources.append(("yahoo", lambda: self._get_yahoo_news(keyword, limit)))

        results = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(func): name for name, func in sources}
            for future in as_completed(futures, timeout=TIMEOUT):
                try:
                    results.extend(future.result())
                except Exception:
                    pass
        return results[:limit]

    def _get_eastmoney_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            url = "https://newsapi.eastmoney.com/kuaixun/v1/getlist_101_ajaxResult_50_1_.html"
            resp = self.session.get(url, timeout=TIMEOUT)
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
        except Exception:
            return []

    def _get_bloomberg_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            url = "https://feeds.bloomberg.com/markets/news.rss"
            resp = self.session.get(url, timeout=TIMEOUT)
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
        except Exception:
            return []

    def _get_ft_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            url = "https://www.ft.com/rss/home"
            resp = self.session.get(url, timeout=TIMEOUT)
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
        except Exception:
            return []

    def _get_yahoo_news(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            url = "https://finance.yahoo.com/markets/news/"
            resp = self.session.get(url, timeout=TIMEOUT)
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
        except Exception:
            return []

    def get_stock_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        symbol_map = {
            "0700.HK": "腾讯", "9988.HK": "阿里巴巴", "600519": "贵州茅台",
            "AAPL": "Apple", "NVDA": "Nvidia", "TSLA": "Tesla",
        }
        keyword = symbol_map.get(symbol, symbol)
        return self.search_news(keyword, source="all", limit=limit)
