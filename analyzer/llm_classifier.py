"""LLM classifier with OpenRouter and keyword fallback."""
import os
from typing import Optional, Dict, Any
import httpx
from config.settings import settings


class LLMClassifier:
    """
    LLM-powered classifier with keyword-based fallback.

    Uses OpenRouter API for LLM calls with DashScope as backup.
    Falls back to keyword-based classification when LLM is unavailable.
    """

    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    DASHSCOPE_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

    def __init__(self):
        self.openrouter_api_key = settings.OPENROUTER_API_KEY or os.environ.get("OPENROUTER_API_KEY", "")
        self.dashscope_api_key = settings.DASHSCOPE_API_KEY or os.environ.get("DASHSCOPE_API_KEY", "")

    def classify_market_sentiment(self, symbol: str, news_text: str) -> str:
        """
        Classify market sentiment from news text.

        Args:
            symbol: Stock symbol
            news_text: News article text

        Returns:
            "positive", "negative", or "neutral"
        """
        prompt = f"""分析以下新闻对 {symbol} 的市场情绪影响，只返回 positive、negative 或 neutral 之一：

新闻：{news_text[:500]}

回复只包含一个词："""

        if self.openrouter_api_key:
            result = self._call_openrouter(prompt)
            if result:
                return result.lower().strip()

        if self.dashscope_api_key:
            result = self._call_dashscope(prompt)
            if result:
                return result.lower().strip()

        return self.classify_with_keyword(news_text, "neutral")

    def _call_openrouter(self, prompt: str) -> Optional[str]:
        """Call OpenRouter API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://stock-trading-assistant",
                "X-Title": "Stock Trading Assistant",
            }
            data = {
                "model": "anthropic/claude-3-haiku",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 50,
            }
            resp = httpx.post(self.OPENROUTER_URL, headers=headers, json=data, timeout=30)
            if resp.status_code == 200:
                result = resp.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"OpenRouter API error: {e}")
        return None

    def _call_dashscope(self, prompt: str) -> Optional[str]:
        """Call DashScope API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.dashscope_api_key}",
                "Content-Type": "application/json",
            }
            data = {
                "model": "qwen-turbo",
                "input": {"prompt": prompt},
                "parameters": {"max_tokens": 50},
            }
            resp = httpx.post(self.DASHSCOPE_URL, headers=headers, json=data, timeout=30)
            if resp.status_code == 200:
                result = resp.json()
                return result["output"]["text"]
        except Exception as e:
            print(f"DashScope API error: {e}")
        return None

    def classify_with_keyword(self, text: str, default: str = "neutral") -> str:
        """
        Keyword-based fallback classification.

        Args:
            text: Text to classify
            default: Default sentiment if no keywords match

        Returns:
            "positive", "negative", or "neutral"
        """
        positive_keywords = ["涨", "大涨", "飙升", "突破", "创新高", "超预期", "利好", "增长", "盈利", "surge", "rise", "gain", "high", "beat", "profit", "growth", "up", "bullish"]
        negative_keywords = ["跌", "大跌", "暴跌", "破发", "创新低", "不及预期", "利空", "亏损", "裁员", "drop", "fall", "crash", "loss", "miss", "layoff", "lawsuit", "down", "bearish", "lawsuit"]

        text_lower = text.lower()
        pos_count = sum(1 for kw in positive_keywords if kw in text_lower)
        neg_count = sum(1 for kw in negative_keywords if kw in text_lower)

        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        return default
