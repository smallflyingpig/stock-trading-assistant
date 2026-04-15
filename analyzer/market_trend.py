"""Market trend analyzer for A/H/US markets."""
from typing import Dict, Any, List
from data_fetcher.yahoo_finance import YahooFinanceFetcher
from data_fetcher.eastmoney import EastMoneyFetcher
from data_fetcher.news_aggregator import NewsAggregator
from data_fetcher.social_media import SocialMediaFetcher


class MarketTrendAnalyzer:
    """Analyze market trends across A/H/US markets."""

    def __init__(self):
        self.yahoo = YahooFinanceFetcher()
        self.eastmoney = EastMoneyFetcher()
        self.news = NewsAggregator()
        self.social = SocialMediaFetcher()

    def analyze_market(self, market: str = "hk") -> Dict[str, Any]:
        """
        Analyze market trend.

        Args:
            market: "a" (A-share), "hk" (HK), or "us" (US)

        Returns:
            Dict with trend analysis.
        """
        if market == "a":
            return self._analyze_a_share()
        elif market == "hk":
            return self._analyze_hk_market()
        elif market == "us":
            return self._analyze_us_market()
        return {"error": "Invalid market"}

    def get_market_news(self, market: str = "all", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get latest market news from all sources.

        Args:
            market: "all", "a", "hk", or "us"
            limit: Number of news items per source

        Returns:
            List of news articles with source and sentiment.
        """
        news_items = []

        # Get news based on market
        if market in ["all", "a"]:
            eastmoney_news = self.news.search_news("A股 市场", source="eastmoney", limit=limit)
            news_items.extend(eastmoney_news)

        if market in ["all", "hk"]:
            hk_news = self.news.search_news("港股 恒生", source="eastmoney", limit=limit)
            news_items.extend(hk_news)

        if market in ["all", "us"]:
            us_news = self.news.search_news("美股 S&P", source="wsj", limit=limit)
            news_items.extend(us_news)

        return news_items[:limit]

    def get_social_sentiment(self, keyword: str = "stock market") -> Dict[str, Any]:
        """
        Get social media sentiment for market.

        Args:
            keyword: Search keyword

        Returns:
            Dict with sentiment data from X.com and Truth Social.
        """
        twitter_sentiment = self.social.get_market_sentiment(keyword)
        truth_social_posts = self.social.get_truth_social_posts(keyword, limit=5)

        return {
            "twitter": twitter_sentiment,
            "truth_social": truth_social_posts,
            "keyword": keyword,
        }

    def _analyze_a_share(self) -> Dict[str, Any]:
        """Analyze A-share market."""
        indices = self.eastmoney.get_market_indices()
        sector_flow = self.eastmoney.get_sector_fund_flow()

        trends = [idx.get("change_percent", 0) for idx in indices.values()]
        avg_change = sum(trends) / len(trends) if trends else 0

        trend = "neutral"
        if avg_change > 1:
            trend = "bullish"
        elif avg_change < -1:
            trend = "bearish"

        return {
            "market": "a-share",
            "trend": trend,
            "indices": indices,
            "avg_change_percent": avg_change,
            "hot_sectors": sector_flow[:5] if sector_flow else [],
        }

    def _analyze_hk_market(self) -> Dict[str, Any]:
        """Analyze HK market."""
        indices_data = []
        for symbol in ["^HSI"]:
            idx = self.yahoo.get_market_index(symbol)
            if idx:
                indices_data.append(idx)

        trend = "neutral"
        if indices_data:
            changes = [idx.get("change_percent", 0) for idx in indices_data]
            avg_change = sum(changes) / len(changes)
            if avg_change > 1:
                trend = "bullish"
            elif avg_change < -1:
                trend = "bearish"

        return {
            "market": "hk",
            "trend": trend,
            "indices": indices_data,
            "avg_change_percent": sum(idx.get("change_percent", 0) for idx in indices_data) / len(indices_data) if indices_data else 0,
        }

    def _analyze_us_market(self) -> Dict[str, Any]:
        """Analyze US market."""
        indices_data = []
        for symbol in ["^GSPC", "^DJI", "^IXIC"]:
            idx = self.yahoo.get_market_index(symbol)
            if idx:
                indices_data.append(idx)

        trend = "neutral"
        if indices_data:
            changes = [idx.get("change_percent", 0) for idx in indices_data]
            avg_change = sum(changes) / len(changes)
            if avg_change > 1:
                trend = "bullish"
            elif avg_change < -1:
                trend = "bearish"

        return {
            "market": "us",
            "trend": trend,
            "indices": indices_data,
            "avg_change_percent": sum(idx.get("change_percent", 0) for idx in indices_data) / len(indices_data) if indices_data else 0,
        }
