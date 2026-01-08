def calculate_risk_score(portfolio: dict) -> dict:
    """
    Calculates a Production-Grade Risk Score (0-100).
    Formula Breakdown:
    - Sector Concentration (35%)
    - Top Holdings Concentration (30%)
    - Diversification Count (20%)
    - Drawdown Sensitivity (15%)
    """
    
    # Data Extraction
    sector_alloc = portfolio.get('sector_allocation', {})
    holdings = portfolio.get('holdings', [])
    holdings_count = portfolio.get('holdings_count', 0)
    total_value = portfolio.get('total_value', 1)
    
    # 1. Sector Risk (35%)
    # Logic: High sector exposure = High risk
    top_sector_pct = max(sector_alloc.values()) if sector_alloc else 0
    if top_sector_pct <= 20:
        sector_risk = 5
    elif top_sector_pct <= 30:
        sector_risk = 15
    else:
        sector_risk = 30 # Max penalty for >30% concentration

    # 2. Concentration Risk (30%)
    # Logic: Top 5 holdings dominance
    sorted_holdings = sorted(holdings, key=lambda x: x['value'], reverse=True)
    top_5_val = sum(h['value'] for h in sorted_holdings[:5])
    top_5_pct = (top_5_val / total_value * 100) if total_value > 0 else 0
    
    if top_5_pct <= 35:
        concentration_risk = 8
    elif top_5_pct <= 45:
        concentration_risk = 18
    else:
        concentration_risk = 28

    # 3. Diversification Risk (20%)
    # Logic: Few stocks < 15 is risky
    if holdings_count >= 25:
        diversification_risk = 5
    elif holdings_count >= 15:
        diversification_risk = 12
    else:
        diversification_risk = 18

    # 4. Drawdown Sensitivity (15%)
    # Proxy: Combine sector and concentration risk
    drawdown_risk = min(15, int((sector_risk + concentration_risk) * 0.25))

    # Total Score
    risk_score = sector_risk + concentration_risk + diversification_risk + drawdown_risk
    
    # Labeling
    if risk_score <= 30:
        label = "Conservative"
    elif risk_score <= 60:
        label = "Moderate"
    else:
        label = "Aggressive"

    # Explainability (Reasons)
    reasons = []
    if top_sector_pct > 25:
        max_sec = max(sector_alloc, key=sector_alloc.get)
        reasons.append(f"{max_sec} sector exposure at {round(top_sector_pct)}%")
    
    if top_5_pct > 40:
        reasons.append(f"Top 5 stocks control {round(top_5_pct)}% of portfolio")
        
    if holdings_count < 15:
        reasons.append(f"Low diversification ({holdings_count} holdings)")
        
    if not reasons:
        reasons.append("Balanced portfolio structure")

    return {
        "risk_score": risk_score,
        "risk_label": label,
        "risk_reasons": reasons,
        "metrics": {
            "top_sector_pct": round(top_sector_pct, 2),
            "top_5_stock_pct": round(top_5_pct, 2),
            "holdings_count": holdings_count
        }
    }

def check_concentration_alerts(portfolio: dict) -> list:
    """
    Returns a list of specific alerts for UI.
    """
    alerts = []
    total_val = portfolio.get('total_value', 1)
    if total_val == 0: return []

    # Check Single Stock Concentration > 15%
    for h in portfolio.get('holdings', []):
        pct = (h['value'] / total_val) * 100
        if pct > 15:
            alerts.append({
                "type": "stock",
                "symbol": h['tradingsymbol'],
                "value": round(pct, 1),
                "message": f"{h['tradingsymbol']} is {round(pct, 1)}% of portfolio (>15%)"
            })

    # Check Sector > 25%
    for sector, pct in portfolio.get('sector_allocation', {}).items():
        if pct > 25:
            alerts.append({
                "type": "sector",
                "symbol": sector,
                "value": round(pct, 1),
                "message": f"{sector} sector is {round(pct, 1)}% of portfolio (>25%)"
            })
            
    return alerts
