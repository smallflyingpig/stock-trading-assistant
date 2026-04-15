"""Portfolio analyzer for user holdings analysis."""
from typing import List, Dict, Any
from data_fetcher.yahoo_finance import YahooFinanceFetcher
from data_fetcher.eastmoney import EastMoneyFetcher
from data_fetcher.news_aggregator import NewsAggregator
from analyzer.llm_classifier import LLMClassifier


class PortfolioAnalyzer:
    """Analyze user portfolio and provide suggestions."""

    def __init__(self):
        self.yahoo = YahooFinanceFetcher()
        self.eastmoney = EastMoneyFetcher()
        self.news = NewsAggregator()
        self.llm = LLMClassifier()

    def analyze_portfolio(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze portfolio holdings.

        Args:
            holdings: List of holdings, each with symbol, shares, cost

        Returns:
            Portfolio analysis with P&L, suggestions, etc.
        """
        analyzed_holdings = []
        total_value = 0
        total_cost = 0
        total_pnl = 0

        for holding in holdings:
            symbol = holding["symbol"]
            shares = holding["shares"]
            cost = holding["cost"]

            # Get current quote based on market
            if symbol.endswith(".HK"):
                quote = self.yahoo.get_stock_quote(symbol)
            elif symbol.startswith(("6", "0", "3")):
                quote = self.eastmoney.get_stock_quote(symbol)
            else:
                quote = self.yahoo.get_stock_quote(symbol)

            if quote:
                current_price = quote.get("current_price", 0)
                currency = quote.get("currency", "HKD")
                current_value = current_price * shares
                cost_basis = cost * shares
                pnl = current_value - cost_basis
                pnl_percent = (pnl / cost_basis * 100) if cost_basis else 0

                # Get news
                news = self.news.get_stock_news(symbol, limit=3)
                sentiment = self._analyze_sentiment(news)

                analyzed_holdings.append({
                    "symbol": symbol,
                    "shares": shares,
                    "cost_per_share": cost,
                    "current_price": current_price,
                    "current_value": current_value,
                    "cost_basis": cost_basis,
                    "pnl": pnl,
                    "pnl_percent": pnl_percent,
                    "currency": currency,
                    "news": news[:2],
                    "sentiment": sentiment,
                })

                total_value += current_value
                total_cost += cost_basis
                total_pnl += pnl

        return {
            "holdings": analyzed_holdings,
            "total_value": total_value,
            "total_cost": total_cost,
            "total_pnl": total_pnl,
            "total_pnl_percent": (total_pnl / total_cost * 100) if total_cost else 0,
        }

    def _analyze_sentiment(self, news: List[Dict[str, Any]]) -> str:
        """Analyze news sentiment for a stock."""
        if not news:
            return "neutral"
        combined_text = " ".join(n.get("title", "") for n in news)
        return self.llm.classify_market_sentiment("", combined_text)
