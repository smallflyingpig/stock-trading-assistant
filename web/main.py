"""Web dashboard for stock trading assistant."""
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from analyzer.market_trend import MarketTrendAnalyzer
from analyzer.portfolio import PortfolioAnalyzer
from analyzer.trading_advisor import TradingAdvisor
import uvicorn

app = FastAPI(title="Stock Trading Assistant")

templates = Jinja2Templates(directory="web/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main dashboard page."""
    market_analyzer = MarketTrendAnalyzer()
    a_share = market_analyzer.analyze_market("a")
    hk = market_analyzer.analyze_market("hk")
    us = market_analyzer.analyze_market("us")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "a_share": a_share,
        "hk": hk,
        "us": us,
    })


@app.get("/portfolio", response_class=HTMLResponse)
async def portfolio(request: Request):
    """Portfolio analysis page."""
    return templates.TemplateResponse("portfolio.html", {"request": request})


@app.post("/portfolio/analyze")
async def analyze_portfolio(
    holdings: str = Form(...),
):
    """Analyze portfolio from user input."""
    portfolio_analyzer = PortfolioAnalyzer()
    trading_advisor = TradingAdvisor()

    # Parse holdings (simple format: "SYMBOL:SHARES:COST,SYMBOL:SHARES:COST,...")
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

    return {
        "analysis": analysis,
        "advice": advice,
    }


@app.get("/stock/{symbol}", response_class=HTMLResponse)
async def stock_detail(request: Request, symbol: str):
    """Stock detail page."""
    return templates.TemplateResponse("stock.html", {
        "request": request,
        "symbol": symbol,
    })


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
