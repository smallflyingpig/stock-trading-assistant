"""Trading advisor for generating buy/sell/hold suggestions."""
from typing import Dict, Any, List


class TradingAdvisor:
    """
    Generate trading advice based on portfolio analysis and market trends.

    Balanced style: combines fundamental + technical analysis.
    """

    def __init__(self):
        pass

    def generate_advice(self, portfolio_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate trading advice based on portfolio analysis.

        Args:
            portfolio_analysis: Output from PortfolioAnalyzer

        Returns:
            Trading advice with action, reason, and risk level.
        """
        holdings = portfolio_analysis.get("holdings", [])
        total_pnl_percent = portfolio_analysis.get("total_pnl_percent", 0)

        advice_list = []
        overall_action = "持有"
        overall_risk = "medium"

        for holding in holdings:
            symbol = holding["symbol"]
            pnl_percent = holding.get("pnl_percent", 0)
            sentiment = holding.get("sentiment", "neutral")

            # Simple rule-based advice
            if pnl_percent > 15 and sentiment == "negative":
                action = "减仓"
                risk = "high"
            elif pnl_percent > 10 and sentiment == "positive":
                action = "持有"
                risk = "medium"
            elif pnl_percent < -10:
                action = "关注"
                risk = "high"
            elif sentiment == "positive":
                action = "持有/加仓"
                risk = "medium"
            elif sentiment == "negative":
                action = "减仓"
                risk = "high"
            else:
                action = "持有"
                risk = "medium"

            advice_list.append({
                "symbol": symbol,
                "action": action,
                "risk": risk,
                "pnl_percent": pnl_percent,
                "sentiment": sentiment,
            })

        # Overall portfolio advice
        if total_pnl_percent > 20:
            overall_action = "考虑部分止盈"
        elif total_pnl_percent < -15:
            overall_action = "关注超跌机会"
        else:
            overall_action = "维持当前仓位"

        return {
            "overall_action": overall_action,
            "overall_risk": overall_risk,
            "holdings_advice": advice_list,
            "total_pnl_percent": total_pnl_percent,
        }
