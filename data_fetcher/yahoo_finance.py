"""Yahoo Finance data fetcher for HK and US stocks."""
import yfinance as yf
from typing import Optional, Dict, Any


class YahooFinanceFetcher:
    """Fetch real-time quotes and market data from Yahoo Finance."""

    def get_stock_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get real-time quote for a stock symbol.

        Args:
            symbol: Stock symbol (e.g., "0700.HK" for Tencent, "AAPL" for Apple)

        Returns:
            Dict with current_price, change, change_percent, volume, etc.
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            price_info = ticker.history(period="1d", interval="1m")

            if price_info.empty:
                return None

            last_price = price_info["Close"].iloc[-1]
            prev_close = info.last_price - info.last_change if hasattr(info, 'last_change') else price_info["Close"].iloc[0]

            return {
                "symbol": symbol,
                "current_price": float(last_price),
                "prev_close": float(prev_close),
                "change": float(last_price - prev_close),
                "change_percent": float((last_price - prev_close) / prev_close * 100) if prev_close else 0,
                "volume": int(info.last_volume) if hasattr(info, 'last_volume') else 0,
                "market_cap": getattr(info, 'market_cap', None),
                "currency": getattr(info, 'currency', 'USD'),
            }
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return None

    def get_market_index(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get market index data.

        Args:
            symbol: Index symbol (e.g., "^HSI" for Hang Seng, "^GSPC" for S&P 500)

        Returns:
            Dict with index data.
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            price_info = ticker.history(period="1d", interval="1m")

            if price_info.empty:
                return None

            last_price = price_info["Close"].iloc[-1]
            prev_close = price_info["Open"].iloc[0]

            return {
                "symbol": symbol,
                "current_price": float(last_price),
                "prev_close": float(prev_close),
                "change": float(last_price - prev_close),
                "change_percent": float((last_price - prev_close) / prev_close * 100) if prev_close else 0,
            }
        except Exception as e:
            print(f"Error fetching index {symbol}: {e}")
            return None

    def get_historical_data(self, symbol: str, period: str = "1mo") -> Optional[Dict[str, Any]]:
        """
        Get historical price data.

        Args:
            symbol: Stock symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 5y, max)

        Returns:
            Dict with OHLCV data.
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            if hist.empty:
                return None
            return {
                "symbol": symbol,
                "dates": hist.index.tolist(),
                "open": hist["Open"].tolist(),
                "high": hist["High"].tolist(),
                "low": hist["Low"].tolist(),
                "close": hist["Close"].tolist(),
                "volume": hist["Volume"].tolist(),
            }
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return None
