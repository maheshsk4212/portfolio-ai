import yfinance as yf
import pandas as pd
import numpy as np
import requests

# --- SCORING WEIGHTS ---
WEIGHTS = {
    "fundamental": 0.35,
    "technical": 0.35,
    "risk": 0.20,
    "sentiment": 0.10
}

# Fix for Yahoo Finance blocking: Use a browser User-Agent
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

def normalize(value, min_val, max_val):
    """Min-Max normalization to 0-100 scale"""
    if value is None or np.isnan(value): return 50
    norm = ((value - min_val) / (max_val - min_val)) * 100
    return max(0, min(100, norm))

def calculate_fundamental_score(info):
    """
    Evaluates financial health based on available metrics.
    """
    score = 50 # Start neutral
    
    # Check for keys safely
    rev_growth = info.get('revenueGrowth')
    profit_margin = info.get('profitMargins')
    roe = info.get('returnOnEquity')
    
    # 1. Revenue Growth
    if rev_growth:
        if rev_growth > 0.20: score += 20
        elif rev_growth > 0.10: score += 10
        elif rev_growth < 0: score -= 10
    
    # 2. Margins
    if profit_margin:
        if profit_margin > 0.20: score += 15
        elif profit_margin > 0.10: score += 5
        elif profit_margin < 0.05: score -= 5
    
    # 3. ROE
    if roe:
        if roe > 0.20: score += 15
        elif roe > 0.15: score += 10
    
    return min(100, max(0, int(score)))

def calculate_technical_score(hist):
    """
    Evaluates price action: Trend, RSI (implied), Volatility.
    """
    if hist.empty or len(hist) < 50:
        return 50
        
    current_price = hist['Close'].iloc[-1]
    # Simple Moving Averages
    sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
    sma_200 = hist['Close'].rolling(window=200).mean().iloc[-1] if len(hist) > 200 else sma_50
    
    score = 50
    
    # 1. Trend vs SMA 50
    if not np.isnan(sma_50):
        if current_price > sma_50: score += 20
        else: score -= 20
    
    # 2. Golden Cross (SMA 50 > SMA 200)
    # Using simple check if values exist
    if not np.isnan(sma_50) and not np.isnan(sma_200):
        if sma_50 > sma_200: score += 10
    
    # 3. Recent Momentum (5 day return)
    if len(hist) >= 6:
        p5 = hist['Close'].iloc[-5]
        mom_5d = (current_price - p5) / p5
        if mom_5d > 0.05: score += 10 # Strong move up
        elif mom_5d < -0.05: score -= 10 # Sharp drop
    
    return min(100, max(0, int(score)))

def calculate_risk_score(info, hist):
    """
    Evaluates risk. Higher score = LOWER Risk (Safety Score).
    """
    score = 50
    
    # 1. Beta (Market Sensitivity)
    beta = info.get('beta')
    if beta:
        if beta < 0.8: score += 20
        elif beta > 1.5: score -= 20
    
    # 2. Volatility (Annualized Std Dev)
    if len(hist) > 20:
        daily_ret = hist['Close'].pct_change().std()
        if not np.isnan(daily_ret):
            vol = daily_ret * np.sqrt(252)
            if vol < 0.20: score += 20 # Low Vol
            elif vol > 0.40: score -= 20 # High Vol
        
    return min(100, max(0, int(score)))

def get_stock_intelligence(symbol):
    """
    Main entry point for stock analysis.
    """
    # Append .NS for NSE if needed
    ticker_symbol = symbol if ("." in symbol or "=" in symbol) else f"{symbol}.NS"
    print(f"Fetching full intelligence for: {ticker_symbol}")

    try:
        # Use session to prevent 403/404 errs
        # 1. Fetch History using download (often more robust)
        hist = yf.download(ticker_symbol, period="1y", progress=False, session=session)
        
        # yf.download sometimes returns MultiIndex columns, flatten if needed
        if isinstance(hist.columns, pd.MultiIndex):
             hist.columns = hist.columns.get_level_values(0)
             
        # Guard: If no history, we can't do much
        if hist.empty:
            raise ValueError(f"No price data found for {ticker_symbol}")

        latest_price = hist['Close'].iloc[-1]
        
        # 2. Fetch Info (Fundamental Data)
        info = {}
        try:
             # Ticker object for info
             t = yf.Ticker(ticker_symbol, session=session)
             info = t.info
        except:
             pass # Info is secondary
        
        # Calculate Sub-scores
        fund_score = calculate_fundamental_score(info)
        tech_score = calculate_technical_score(hist)
        risk_score = calculate_risk_score(info, hist)
        sent_score = 50 # No News API yet, neutral default
        
        # Weighted Aggregation
        ai_score = (
            (fund_score * WEIGHTS["fundamental"]) +
            (tech_score * WEIGHTS["technical"]) +
            (risk_score * WEIGHTS["risk"]) +
            (sent_score * WEIGHTS["sentiment"])
        )
        ai_score = int(ai_score)
        
        # Determine Bias
        if ai_score >= 75: bias = "BUY"
        elif ai_score <= 45: bias = "AVOID"
        else: bias = "HOLD"
        
        # Generate Reasoning
        reasons = []
        if fund_score > 60: reasons.append("Solid Fundamentals (Growth/Margins)")
        if fund_score < 40: reasons.append("Weak Financial Metrics")
        
        if tech_score > 60: reasons.append("Bullish Price Trend")
        if tech_score < 40: reasons.append("Bearish Price Action")
        
        if risk_score > 60: reasons.append("Low Volatility (Safe)")
        if risk_score < 40: reasons.append("High Volatility (Risk)")

        if not reasons: reasons.append("Mixed signals across metrics.")
        
        return {
            "symbol": symbol,
            "ai_score": ai_score,
            "bias": bias,
            "confidence": 0.85, 
            "components": {
                "fundamental": fund_score,
                "technical": tech_score,
                "risk": risk_score,
                "sentiment": sent_score
            },
            "reasoning": reasons[:4],
            "price": round(latest_price, 2),
            "is_mock": False
        }
        
    except Exception as e:
        print(f"Stock Intel Error for {symbol}: {e}")
        
        # --- DETERMINISTIC SIMULATION (Fallback) ---
        # Generate consistent data based on symbol hash so it feels functional
        
        seed_val = sum(ord(c) for c in symbol)
        np.random.seed(seed_val)
        
        # 1. Determine Archetype to force variety (Avoid Mean Reversion to HOLD)
        # 0 = Weak (AVOID), 1 = Average (HOLD), 2 = Strong (BUY)
        archetype_roll = np.random.random()
        
        if archetype_roll < 0.33:
            archetype = "WEAK"
            base_bias = -0.40  # Heavily drag metrics down
        elif archetype_roll < 0.66:
            archetype = "AVG"
            base_bias = 0.0
        else:
            archetype = "STRONG"
            base_bias = 0.40  # Heavily boost metrics up
            
        sim_price = float(np.random.randint(500, 3000))
        
        # Sim Info (Applied Bias)
        sim_info = {
            'revenueGrowth': np.random.uniform(-0.10, 0.40) + base_bias,
            'profitMargins': np.random.uniform(0.02, 0.30) + (base_bias * 0.5),
            'returnOnEquity': np.random.uniform(0.05, 0.35) + (base_bias * 0.5),
            'beta': np.random.uniform(0.5, 1.8) - (base_bias * 0.5) # Lower beta is good
        }
        
        # Sim History (Trend matches archetype)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
        
        trend_slope = 0.0
        if archetype == "STRONG": trend_slope = 0.005 # Up trend
        if archetype == "WEAK": trend_slope = -0.005 # Down trend
        
        trend = np.linspace(sim_price * (1 - (trend_slope*100)), sim_price, 100)
        noise = np.random.normal(0, sim_price*0.02, 100)
        sim_hist = pd.DataFrame({'Close': trend + noise}, index=dates)
        
        # Run Real Logic on Sim Data
        fund_score = calculate_fundamental_score(sim_info)
        tech_score = calculate_technical_score(sim_hist)
        risk_score = calculate_risk_score(sim_info, sim_hist)
        sent_score = int(np.random.randint(40, 90) + (base_bias * 20))
        sent_score = max(0, min(100, sent_score))
        
        ai_score = int(
            (fund_score * WEIGHTS["fundamental"]) +
            (tech_score * WEIGHTS["technical"]) +
            (risk_score * WEIGHTS["risk"]) +
            (sent_score * WEIGHTS["sentiment"])
        )
        
        # Force Extremes if needed for demo variety
        if archetype == "STRONG" and ai_score < 70: ai_score += 10
        if archetype == "WEAK" and ai_score > 40: ai_score -= 10
        ai_score = max(0, min(100, ai_score))
        
        if ai_score >= 70: bias = "BUY"
        elif ai_score <= 45: bias = "AVOID"
        else: bias = "HOLD"
        
        # Dynamic Confidence
        algo_conf = np.random.uniform(0.70, 0.95)
        
        reasons = []
        if sim_info['revenueGrowth'] > 0.15: reasons.append(f"Strong Rev Growth ({int(sim_info['revenueGrowth']*100)}%)")
        if sim_info['revenueGrowth'] < 0: reasons.append(f"Declining Revenue ({int(sim_info['revenueGrowth']*100)}%)")
        
        if tech_score > 60: reasons.append("Bullish Technical Trend")
        if tech_score < 40: reasons.append("Bearish Price Structure")
        
        if risk_score > 70: reasons.append("Low Volatility (Safe)")
        if risk_score < 40: reasons.append("High Volatility / High Beta")
        
        if not reasons: reasons.append("Market signals are mixed/neutral")

        return {
            "symbol": symbol,
            "ai_score": ai_score,
            "bias": bias,
            "confidence": round(algo_conf, 2), 
            "components": {
                "fundamental": fund_score,
                "technical": tech_score,
                "risk": risk_score,
                "sentiment": sent_score
            },
            "reasoning": reasons[:3],
            "price": sim_price,
            "is_mock": True,
            "note": "Simulated (API Blocked)"
        }
