import pytest
from data_fetcher.social_media import SocialMediaFetcher

def test_search_twitter():
    """Test searching X.com (Twitter) for financial keywords."""
    fetcher = SocialMediaFetcher()
    tweets = fetcher.search_twitter("AAPL earnings", limit=5)
    assert isinstance(tweets, list)
    assert len(tweets) >= 1

def test_get_market_sentiment():
    """Test getting market sentiment from social media."""
    fetcher = SocialMediaFetcher()
    sentiment = fetcher.get_market_sentiment("tech stocks")
    assert sentiment is not None
    assert "sentiment" in sentiment
    assert sentiment["keyword"] == "tech stocks"
