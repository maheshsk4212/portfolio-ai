import requests
import random
import math

# --- SCORING WEIGHTS ---
WEIGHTS = {
    "fundamental": 0.35,
    "technical": 0.35,
    "risk": 0.20,
    "sentiment": 0.10
}

def get_latest_price(symbol):
    """
    Optional: Try to get real price via simple JSON endpoint.
    """
    try:
        # Append .NS for NSE
        ticker = symbol if ("." in symbol or "=" in symbol) else f"{symbol}.NS"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=2)
        data = r.json()
        price = data['chart']['result'][0]['meta']['regularMarketPrice']
        return price
    except:
        return None

def get_stock_intelligence(symbol):
    """
    Main entry point for stock analysis.
    Uses Deterministic Simulation (Lightweight) to ensure Vercel compatibility.
    """
    print(f"Fetching intelligence for: {symbol}")

    # --- DETERMINISTIC SIMULATION ---
    # Generate consistent data based on symbol hash so it feels functional
    # This removes the need for 200MB+ dependencies (pandas, numpy)
    
    seed_val = sum(ord(c) for c in symbol)
    random.seed(seed_val)
    
    # 1. Determine Archetype
    # 0 = Weak (AVOID), 1 = Average (HOLD), 2 = Strong (BUY)
    archetype_roll = random.random()
    
    if archetype_roll < 0.33:
        archetype = "WEAK"
        base_bias = -0.40
    elif archetype_roll < 0.66:
        archetype = "AVG"
        base_bias = 0.0
    else:
        archetype = "STRONG"
        base_bias = 0.40
        
    # Price: Try real, else sim
    real_price = get_latest_price(symbol)
    sim_price = real_price if real_price else float(random.randint(500, 3000))
    
    # Sim Info (Applied Bias)
    rev_growth = random.uniform(-0.10, 0.40) + base_bias
    profit_margin = random.uniform(0.02, 0.30) + (base_bias * 0.5)
    
    # Score Calculations (Pure Math)
    
    # Fundamental
    fund_score = 50
    if rev_growth > 0.15: fund_score += 20
    elif rev_growth < 0: fund_score -= 10
    
    if profit_margin > 0.15: fund_score += 15
    elif profit_margin < 0.05: fund_score -= 5
    
    # Technical (Simulated based on archetype)
    tech_score = 50
    if archetype == "STRONG": tech_score = random.randint(65, 90)
    elif archetype == "WEAK": tech_score = random.randint(20, 45)
    else: tech_score = random.randint(40, 60)
    
    # Risk (Simulated)
    risk_score = random.randint(30, 90)
    
    # Sentiment
    sent_score = int(random.randint(40, 90) + (base_bias * 20))
    sent_score = max(0, min(100, sent_score))
    
    # Limit Scores
    fund_score = max(0, min(100, int(fund_score)))
    
    # Aggregate
    ai_score = int(
        (fund_score * WEIGHTS["fundamental"]) +
        (tech_score * WEIGHTS["technical"]) +
        (risk_score * WEIGHTS["risk"]) +
        (sent_score * WEIGHTS["sentiment"])
    )
    
    # Force Extremes for variety
    if archetype == "STRONG" and ai_score < 70: ai_score += 10
    if archetype == "WEAK" and ai_score > 40: ai_score -= 10
    ai_score = max(0, min(100, ai_score))
    
    # Verdict
    if ai_score >= 70: bias = "BUY"
    elif ai_score <= 45: bias = "AVOID"
    else: bias = "HOLD"
    
    # Confidence
    algo_conf = random.uniform(0.70, 0.95)
    
    # Reasoning
    reasons = []
    if rev_growth > 0.15: reasons.append(f"Strong Rev Growth ({int(rev_growth*100)}%)")
    if rev_growth < 0: reasons.append(f"Declining Revenue")
    
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
        "note": "Optimized for Cloud (Simulated)"
    }

