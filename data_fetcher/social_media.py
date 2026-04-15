"""Social media data fetcher for X.com (Twitter) and Truth Social."""
from typing import List, Dict, Any, Optional
import requests


class SocialMediaFetcher:
    """
    Fetch social media data for market sentiment analysis.

    Note: X.com (Twitter) API requires authentication. Without a valid API key,
    this module will use web scraping which may be limited by anti-bot measures.
    """

    def __init__(self, twitter_bearer_token: Optional[str] = None):
        self.twitter_bearer_token = twitter_bearer_token
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

    def search_twitter(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search X.com (Twitter) for keyword.

        Args:
            keyword: Search keyword
            limit: Maximum number of results

        Returns:
            List of tweets.
        """
        if not self.twitter_bearer_token:
            return self._search_twitter_web(keyword, limit)

        try:
            url = "https://api.twitter.com/2/tweets/search/recent"
            headers = {"Authorization": f"Bearer {self.twitter_bearer_token}"}
            params = {
                "query": keyword,
                "max_results": min(limit, 100),
                "tweet.fields": "created_at,public_metrics,author_id",
            }
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                tweets = []
                for tweet in data.get("data", []):
                    tweets.append({
                        "id": tweet["id"],
                        "text": tweet["text"],
                        "created_at": tweet.get("created_at"),
                        "likes": tweet.get("public_metrics", {}).get("like_count", 0),
                        "retweets": tweet.get("public_metrics", {}).get("retweet_count", 0),
                        "source": "twitter",
                    })
                return tweets
        except Exception as e:
            print(f"Error searching Twitter: {e}")
        return self._search_twitter_web(keyword, limit)

    def _search_twitter_web(self, keyword: str, limit: int) -> List[Dict[str, Any]]:
        """
        Fallback web scraping for Twitter search results.
        Note: This is a placeholder - full scraping requires API access.
        """
        return [{
            "text": f"X.com search for '{keyword}' - API key required for full access",
            "source": "twitter_web",
            "keyword": keyword,
        }]

    def get_market_sentiment(self, keyword: str) -> Dict[str, Any]:
        """
        Get market sentiment for a keyword from social media.

        Args:
            keyword: Market or stock keyword

        Returns:
            Dict with sentiment analysis.
        """
        tweets = self.search_twitter(keyword, limit=20)

        if not tweets:
            return {"sentiment": "neutral", "keyword": keyword, "data_source": "none"}

        total_engagement = sum(t.get("likes", 0) + t.get("retweets", 0) for t in tweets)
        avg_engagement = total_engagement / len(tweets) if tweets else 0

        if avg_engagement > 1000:
            sentiment = "positive"
        elif avg_engagement > 100:
            sentiment = "neutral"
        else:
            sentiment = "negative"

        return {
            "sentiment": sentiment,
            "keyword": keyword,
            "tweet_count": len(tweets),
            "avg_engagement": avg_engagement,
            "data_source": "twitter" if self.twitter_bearer_token else "twitter_web",
        }

    def get_truth_social_posts(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get posts from Truth Social related to keyword.

        Note: Truth Social has limited public API access.
        """
        return [{
            "text": f"Truth Social search for '{keyword}' - limited public access",
            "source": "truth_social",
            "keyword": keyword,
        }]
