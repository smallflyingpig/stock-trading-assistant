"""News aggregator for Chinese and international financial news."""
import requests
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
            source: "caixin", "wsj", "eastmoney", or "all"
            limit: Maximum number of results

        Returns:
            List of news articles.
        """
        if source == "caixin" or source == "all":
            return self._search_caixin(keyword, limit)
        elif source == "wsj" or source == "all":
            return self._search_wsj(keyword, limit)
        elif source == "eastmoney" or source == "all":
            return self._search_eastmoney(keyword, limit)
        return []

    def _search_caixin(self, keyword: str, limit: int) -> List[Dict[str, Any]]:
        """Search Caixin news."""
        try:
            url = "https://gateway.caixin.com/api/search/searchAll"
            params = {
                "query": keyword,
                "page": 1,
                "size": limit,
                "type": "article",
            }
            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                articles = []
                for item in data.get("data", {}).get("list", [])[:limit]:
                    articles.append({
                        "source": "caixin",
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "time": item.get("time", ""),
                        "summary": item.get("summary", ""),
                    })
                return articles
            return []
        except Exception as e:
            print(f"Error searching Caixin: {e}")
            return []

    def _search_wsj(self, keyword: str, limit: int) -> List[Dict[str, Any]]:
        """Search WSJ news."""
        try:
            url = "https://www.wsj.com/search/term.html"
            params = {
                "keyword": keyword,
            }
            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                return [{
                    "source": "wsj",
                    "title": f"WSJ: {keyword}",
                    "url": resp.url,
                    "time": datetime.now().isoformat(),
                }]
            return []
        except Exception as e:
            print(f"Error searching WSJ: {e}")
            return []

    def _search_eastmoney(self, keyword: str, limit: int) -> List[Dict[str, Any]]:
        """Search EastMoney news."""
        try:
            url = "https://search-api-web.eastmoney.com/search/jsonp"
            json_param = '{"uid":"","keyword":"' + keyword + '","type":["cmsArticle"],"client":"web","clientType":"pc","clientVersion":"curr","param":{"searchScope":"default","sort":"default","pageIndex":1,"pageSize":' + str(limit) + ',"preTag":"<em>","postTag":"</em>"}}'
            params = {"param": json_param}
            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                return [{
                    "source": "eastmoney",
                    "title": f"东方财富: {keyword}",
                    "url": "",
                    "time": datetime.now().isoformat(),
                }]
            return []
        except Exception as e:
            print(f"Error searching EastMoney: {e}")
            return []

    def get_stock_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get news related to a specific stock.

        Args:
            symbol: Stock symbol (e.g., "0700.HK", "600519", "AAPL")
            limit: Maximum number of results

        Returns:
            List of news articles.
        """
        # Map symbol to company name for search
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
