import pytest
from data_fetcher.eastmoney import EastMoneyFetcher

def test_get_a_share_quote():
    """Test fetching A-share quote."""
    fetcher = EastMoneyFetcher()
    # 600519 = Kweichow Moutai
    quote = fetcher.get_stock_quote("600519")
    assert quote is not None
    assert quote["symbol"] == "600519"
    assert "current_price" in quote

def test_get_market_indices():
    """Test fetching A-share market indices."""
    fetcher = EastMoneyFetcher()
    indices = fetcher.get_market_indices()
    assert indices is not None
    assert len(indices) > 0

def test_get_sector_fund_flow():
    """Test fetching sector fund flow data."""
    fetcher = EastMoneyFetcher()
    flow = fetcher.get_sector_fund_flow()
    assert flow is not None
    assert isinstance(flow, list)
