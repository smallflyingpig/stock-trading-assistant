import pytest
from data_fetcher.news_aggregator import NewsAggregator

def test_search_news():
    """Test searching news."""
    aggregator = NewsAggregator()
    news = aggregator.search_news("腾讯", source="eastmoney", limit=5)
    assert isinstance(news, list)

def test_get_stock_news():
    """Test getting news for a specific stock."""
    aggregator = NewsAggregator()
    news = aggregator.get_stock_news("0700.HK", limit=5)
    assert isinstance(news, list)
