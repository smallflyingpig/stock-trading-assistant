"""Market trend analyzer for A/H/US markets."""
from typing import Dict, Any
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
        for symbol in ["^HSI"]:  # ^HSTECH may not be available
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
