from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
from pathlib import Path
from zerodha import get_portfolio_summary, set_access_token, get_login_url, generate_session
from ai_brain import analyze_portfolio
from scheduler import start_scheduler
from models import PortfolioSnapshot, AIAnalysisResponse, AIRequest
from risk_engine import calculate_risk_score, check_concentration_alerts
from market_engine import get_market_context
from stock_engine import get_stock_intelligence
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Portfolio Brain")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TokenRequest(BaseModel):
    access_token: str

@app.on_event("startup")
def startup_event():
    start_scheduler()

@app.get("/")
def health():
    return {"status": "AI Portfolio Backend Running"}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    html_path = Path(__file__).parent / "dashboard.html"
    return html_path.read_text()

@app.get("/zerodha/login")
def zerodha_login():
    return RedirectResponse(get_login_url())

@app.get("/zerodha/callback")
def zerodha_callback(request: Request):
    request_token = request.query_params.get("request_token")
    
    if not request_token:
        return {"error": "Request token missing", "status": "failed"}

    # Generate persistent token
    access_token = generate_session(request_token)
    
    if access_token:
        # Redirect to Dashboard with Token (Stateless Handshake)
        return RedirectResponse(url=f"/dashboard?access_token={access_token}")
        
    return {"status": "error", "message": "Failed to generate token"}

@app.get("/login-url")
def login_link():
    """Returns the Zerodha login URL."""
    return {"login_url": get_login_url()}

@app.post("/set-token")
def update_token(req: TokenRequest):
    """Manually set the access token for the day."""
    set_access_token(req.access_token)
    return {"status": "Token updated"}

# --- NEW ENDPOINTS (AI-Sector Phase 1) ---

@app.get("/stock/{symbol}/intelligence")
def stock_intel(symbol: str):
    """
    Returns AI Score, Bias, and Component Breakdown for a specific stock.
    Example: /stock/RELIANCE/intelligence
    """
    return get_stock_intelligence(symbol)

@app.get("/market/mood")
def market_mood():
    """
    Returns the current market regime and signals (VIX, Yields, etc.).
    Alias for /market-context.
    """
    return get_market_context()

@app.get("/market-context")
def market_context():
    return get_market_context()

@app.get("/portfolio")
def portfolio():
    data = get_portfolio_summary()
    
    # Dynamic Risk Status based on Market Regime
    try:
        from market_engine import get_market_context
        ctx = get_market_context()
        regime = ctx.get("regime", "NORMAL")
        
        if regime == "NORMAL":
            data["risk_status"] = "Low"
        elif regime == "ELEVATED_VOLATILITY":
            data["risk_status"] = "Moderate"
        else:
            data["risk_status"] = "High"
    except:
        data["risk_status"] = "Moderate" # Fallback
        
    return data

from risk_engine import calculate_risk_score, check_concentration_alerts
from market_engine import get_market_context

# ...

@app.post("/ai-analysis", response_model=AIAnalysisResponse)
def ai_analysis(req: AIRequest = None):
    portfolio_data = get_portfolio_summary()
    
    # Calculate Risk & Alerts
    risk_data = calculate_risk_score(portfolio_data)
    alerts = check_concentration_alerts(portfolio_data)
    
    # Get Market Regime
    market_data = get_market_context()
    
    question = req.question if req else None
    
    # Pass risk & market info to AI
    analysis = analyze_portfolio(portfolio_data, question=question, risk_data=risk_data, alerts=alerts, market_data=market_data)
    return {"analysis": analysis}
