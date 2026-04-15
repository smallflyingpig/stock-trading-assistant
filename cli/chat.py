"""CLI chat interface for stock trading assistant."""
import re
from typing import Dict, Any, List
from analyzer.market_trend import MarketTrendAnalyzer
from analyzer.portfolio import PortfolioAnalyzer
from analyzer.trading_advisor import TradingAdvisor


class CLIChat:
    """
    Command-line chat interface for stock trading assistant.

    Supports commands:
    - 大盘今天怎么样？ → Market trend analysis
    - 分析腾讯控股 0700.HK → Single stock analysis
    - 我有腾讯500股，成本350港币 → Portfolio input
    - 今天涨跌幅前十的板块？ → Sector analysis
    """

    def __init__(self):
        self.market_analyzer = MarketTrendAnalyzer()
        self.portfolio_analyzer = PortfolioAnalyzer()
        self.trading_advisor = TradingAdvisor()
        self.portfolio: List[Dict[str, Any]] = []

    def parse_intent(self, text: str) -> Dict[str, Any]:
        """
        Parse user input to determine intent.

        Args:
            text: User input text

        Returns:
            Dict with intent type and extracted parameters.
        """
        text = text.strip()

        # Market query patterns
        if any(kw in text for kw in ["大盘", "今天怎么样", "市场", "行情"]):
            return {"type": "market_query", "params": self._extract_market(text)}

        # Portfolio input patterns
        if any(kw in text for kw in ["我有", "持仓", "成本", "股"]):
            return {"type": "portfolio_input", "params": self._extract_holdings(text)}

        # Single stock analysis patterns
        if re.search(r"\d{4}\.HK|[A-Z]{2,5}", text):
            match = re.search(r"\d{4}\.HK|[A-Z]{2,5}", text)
            if match:
                return {"type": "stock_analysis", "params": {"symbol": match.group()}}

        # Sector analysis
        if any(kw in text for kw in ["板块", "涨跌幅", "排行"]):
            return {"type": "sector_analysis", "params": {}}

        return {"type": "unknown", "params": {}}

    def _extract_market(self, text: str) -> Dict[str, str]:
        """Extract market identifier from text."""
        if "A股" in text or "沪深" in text or "上证" in text:
            return {"market": "a"}
        elif "港股" in text or "恒生" in text:
            return {"market": "hk"}
        elif "美股" in text or "纳斯达克" in text or "标普" in text:
            return {"market": "us"}
        return {"market": "hk"}

    def _extract_holdings(self, text: str) -> Dict[str, Any]:
        """
        Extract holdings from text.

        Example: "我有腾讯500股，成本350港币"
        """
        holdings = []
        # Pattern: name + number + 股 + ... + 成本 + number
        pattern = r"([\u4e00-\u9fa5a-zA-Z]+)(\d+)股.*?成本(\d+(?:\.\d+)?)"
        for match in re.finditer(pattern, text):
            name = match.group(1)
            shares = int(match.group(2))
            cost = float(match.group(3))
            holdings.append({"name": name, "shares": shares, "cost": cost})

        return {"holdings": holdings}

    def chat(self, user_input: str) -> str:
        """
        Process user input and return response.

        Args:
            user_input: User message

        Returns:
            Response string.
        """
        intent = self.parse_intent(user_input)

        if intent["type"] == "market_query":
            market = intent["params"]["market"]
            analysis = self.market_analyzer.analyze_market(market)
            return self._format_market_response(analysis)

        elif intent["type"] == "portfolio_input":
            holdings = intent["params"]["holdings"]
            self.portfolio.extend(holdings)
            analysis = self.portfolio_analyzer.analyze_portfolio(self.portfolio)
            advice = self.trading_advisor.generate_advice(analysis)
            return self._format_portfolio_response(analysis, advice)

        elif intent["type"] == "stock_analysis":
            symbol = intent["params"]["symbol"]
            return f"分析 {symbol} 的详细数据..."

        elif intent["type"] == "sector_analysis":
            analysis = self.market_analyzer.analyze_market("a")
            return self._format_sector_response(analysis.get("hot_sectors", []))

        return "抱歉，我不太理解你的问题。请试试：\n- 大盘今天怎么样？\n- 我有腾讯500股，成本350港币"

    def _format_market_response(self, analysis: Dict[str, Any]) -> str:
        """Format market analysis as readable text."""
        trend = analysis.get("trend", "neutral")
        avg_change = analysis.get("avg_change_percent", 0)

        emoji = {"bullish": "📈", "bearish": "📉", "neutral": "➡️"}.get(trend, "➡️")
        trend_text = {"bullish": "多头", "bearish": "空头", "neutral": "震荡"}.get(trend, "震荡")

        lines = [
            f"{emoji} 市场趋势：{trend_text}",
            f"平均涨跌幅：{avg_change:+.2f}%",
        ]

        if "indices" in analysis:
            for idx in analysis["indices"]:
                symbol = idx.get("symbol", "")
                price = idx.get("current_price", 0)
                change = idx.get("change_percent", 0)
                lines.append(f"  {symbol}: {price:.2f} ({change:+.2f}%)")

        return "\n".join(lines)

    def _format_portfolio_response(self, analysis: Dict[str, Any], advice: Dict[str, Any]) -> str:
        """Format portfolio analysis as readable text."""
        lines = [
            f"📊 持仓分析",
            f"总市值：{analysis['total_value']:.2f}",
            f"总盈亏：{analysis['total_pnl']:.2f} ({analysis['total_pnl_percent']:+.2f}%)",
            f"",
            f"个股明细：",
        ]

        for h in analysis["holdings"]:
            lines.append(
                f"  {h['symbol']}: {h['current_price']:.2f} x {h['shares']} = {h['current_value']:.2f} "
                f"({h['pnl_percent']:+.2f}%)"
            )

        lines.append(f"")
        lines.append(f"💡 建议：{advice['overall_action']}")

        return "\n".join(lines)

    def _format_sector_response(self, sectors: list) -> str:
        """Format sector analysis as readable text."""
        if not sectors:
            return "暂无板块数据"
        lines = ["📊 热门板块："]
        for s in sectors[:10]:
            name = s.get("name", "")
            inflow = s.get("net_inflow", 0)
            lines.append(f"  {name}: 主力净流入 {inflow:.2f}亿")
        return "\n".join(lines)
