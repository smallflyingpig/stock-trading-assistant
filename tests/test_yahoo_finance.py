import pytest
from data_fetcher.yahoo_finance import YahooFinanceFetcher

def test_get_stock_quote_us():
    """Test fetching US stock quote."""
    fetcher = YahooFinanceFetcher()
    quote = fetcher.get_stock_quote("AAPL")
    assert quote is not None
    assert quote["symbol"] == "AAPL"
    assert "current_price" in quote

def test_get_market_index():
    """Test fetching market index."""
    fetcher = YahooFinanceFetcher()
    index = fetcher.get_market_index("^GSPC")
    assert index is not None
    assert "current_price" in index
