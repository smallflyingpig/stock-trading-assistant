"""Web dashboard for stock trading assistant."""
import json
from pathlib import Path
from datetime import date
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from analyzer.market_trend import MarketTrendAnalyzer
from analyzer.portfolio import PortfolioAnalyzer
from analyzer.trading_advisor import TradingAdvisor
import uvicorn

app = FastAPI(title="Stock Trading Assistant")
templates = Jinja2Templates(directory="web/templates")
DB_PATH = Path("/home/jiguo/workspace/stock-trading-assistant/data/daily_cache.db")


def load_cached_data():
    """Load today's cached data from SQLite."""
    import sqlite3
    if not DB_PATH.exists():
        return None
    try:
        conn = sqlite3.connect(DB_PATH)
        today = date.today().isoformat()
        # Get latest market snapshots
        markets = {}
        for market in ["a-share", "hk", "us"]:
            row = conn.execute(
                "SELECT data FROM market_snapshots WHERE date=? AND market=? ORDER BY created_at DESC LIMIT 1",
                (today, market)
            ).fetchone()
            if row:
                markets[market] = json.loads(row[1])

        # Get news
        row = conn.execute(
            "SELECT data FROM news_cache WHERE date=? ORDER BY created_at DESC LIMIT 1",
            (today,)
        ).fetchone()
        news = json.loads(row[0]) if row else []

        conn.close()
        if markets or news:
            return {"markets": markets, "news": news}
    except Exception:
        pass
    return None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main dashboard - shows cached data immediately, refresh in background."""
    cached = load_cached_data()

    # Return cached data for fast page load
    if cached:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "a_share": cached["markets"].get("a-share", {}),
            "hk": cached["markets"].get("hk", {}),
            "us": cached["markets"].get("us", {}),
            "news": cached.get("news", []),
            "social_sentiment": {"twitter": {"sentiment": "cached", "tweet_count": 0, "avg_engagement": 0, "data_source": "cache"}},
            "from_cache": True,
        })

    # No cache - return empty state (will populate on refresh)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "a_share": {"trend": "unknown", "avg_change_percent": 0, "indices": {}},
        "hk": {"trend": "unknown", "avg_change_percent": 0, "indices": []},
        "us": {"trend": "unknown", "avg_change_percent": 0, "indices": []},
        "news": [],
        "social_sentiment": None,
        "from_cache": False,
    })


@app.get("/api/refresh")
async def refresh_data():
    """Fetch fresh data and return JSON (called by browser on page load)."""
    analyzer = MarketTrendAnalyzer()
    a_share = analyzer.analyze_market("a")
    hk = analyzer.analyze_market("hk")
    us = analyzer.analyze_market("us")
    news = analyzer.get_market_news("all", limit=15)
    social = analyzer.get_social_sentiment("stock market")

    return JSONResponse({
        "a_share": a_share,
        "hk": hk,
        "us": us,
        "news": news,
        "social_sentiment": social,
    })


@app.get("/portfolio", response_class=HTMLResponse)
async def portfolio(request: Request):
    return templates.TemplateResponse("portfolio.html", {"request": request})


@app.post("/portfolio/analyze")
async def analyze_portfolio(holdings: str = Form(...)):
    portfolio_analyzer = PortfolioAnalyzer()
    trading_advisor = TradingAdvisor()

    parsed_holdings = []
    for item in holdings.split(","):
        parts = item.strip().split(":")
        if len(parts) == 3:
            parsed_holdings.append({
                "symbol": parts[0].strip(),
                "shares": int(parts[1]),
                "cost": float(parts[2]),
            })

    if not parsed_holdings:
        return {"error": "Invalid format. Use: SYMBOL:SHARES:COST,SYMBOL:SHARES:COST"}

    analysis = portfolio_analyzer.analyze_portfolio(parsed_holdings)
    advice = trading_advisor.generate_advice(analysis)
    return {"analysis": analysis, "advice": advice}


@app.get("/stock/{symbol}", response_class=HTMLResponse)
async def stock_detail(request: Request, symbol: str):
    return templates.TemplateResponse("stock.html", {"request": request, "symbol": symbol})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
