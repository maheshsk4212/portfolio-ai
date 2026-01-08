import time
import requests
import random
from datetime import datetime, timedelta

# --- CACHE MECHANISM ---
class MarketDataCache:
    def __init__(self, ttl_minutes=15):
        self.ttl = ttl_minutes * 60
        self.data = None
        self.last_updated = 0

    def get(self):
        if self.data and (time.time() - self.last_updated < self.ttl):
            return self.data
        return None

    def set(self, data):
        self.data = data
        self.last_updated = time.time()

market_cache = MarketDataCache(ttl_minutes=15)

def fetch_live_signals():
    """
    Simulates live market data (Lightweight for Vercel).
    """
    try:
        # --- ROBUST SIMULATION ---
        # Generate dynamic market conditions.
        
        # 1. Randomize "Stress Level" (0=Calm, 1=Nervous, 2=Panic)
        stress_seed = random.random()
        
        sim_vix = 14.0
        drawdown = 2.0
        
        if stress_seed < 0.6: # Calm
             sim_vix = random.uniform(11, 16)
             drawdown = random.uniform(0, 3)
             yield_trend = "STABLE"
        elif stress_seed < 0.9: # Caution
             sim_vix = random.uniform(17, 22)
             drawdown = random.uniform(3, 8)
             yield_trend = "UP"
        else: # Panic/Stress
             sim_vix = random.uniform(23, 35)
             drawdown = random.uniform(8, 15)
             yield_trend = "UP"
             
        return {
            "vix": round(sim_vix, 2),
            "index_drawdown": round(drawdown, 2),
            "interest_rates_trend": "STABLE",
            "bond_yields_trend": yield_trend,
            "oil_prices_trend": random.choice(["UP", "DOWN", "STABLE"]),
            "market_index": 24500.00,
            "is_simulated": True
        }

    except Exception as e:
        print(f"Error in simulation: {e}")
        return {
            "vix": 15.0,
            "index_drawdown": 0.0,
            "interest_rates_trend": "STABLE",
            "bond_yields_trend": "STABLE",
            "oil_prices_trend": "STABLE",
            "market_index": 24500.00,
            "is_simulated": True
        }

def get_macro_signals():
    # Check cache first
    cached = market_cache.get()
    if cached:
        return cached
    
    # Fetch live
    signals = fetch_live_signals()
    market_cache.set(signals)
    return signals

def determine_regime(signals):
    """
    Regime Scoring Logic (Same as specified):
    +1 for each stress indicator
    """
    score = 0
    if signals.get('vix', 0) > 20: score += 1
    if signals.get('index_drawdown', 0) > 5.0: score += 1
    if signals.get('interest_rates_trend') == 'UP': score += 1
    if signals.get('bond_yields_trend') == 'UP': score += 1
    
    if score == 0: return "NORMAL", ["Market indicators are stable."]
    if score <= 2: return "ELEVATED_VOLATILITY", ["Volatility or drawdown detected."]
    return "STAGFLATION_RISK", ["High volatility and negative trend confluence."]

def get_sector_impacts(regime, signals):
    """
    Returns specific sector advice based on regime.
    """
    impacts = {}
    
    bond_yields_trend = signals.get('bond_yields_trend', 'STABLE')
    oil_prices_trend = signals.get('oil_prices_trend', 'STABLE')
    
    if regime == 'NORMAL':
        impacts['Technology'] = 'Positive (Risk On)'
        impacts['Financials'] = 'Positive (Credit Growth)'
        impacts['Healthcare'] = 'Neutral'
        
    elif regime == 'ELEVATED_VOLATILITY':
        impacts['Technology'] = 'Negative (Valuation Pressure)' if bond_yields_trend == 'UP' else 'Neutral'
        impacts['FMCG'] = 'Positive (Defensive Rotation)'
        impacts['Pharma'] = 'Positive (Safety)'
        
    else: # STAGFLATION/STRESS
        impacts['Technology'] = 'Negative (High Risk)'
        impacts['Financials'] = 'Negative (NPA Risks)'
        impacts['Metals'] = 'Positive (Inflation Hedge)'
        
    # Oil Specific
    if oil_prices_trend == 'UP':
        impacts['Oil & Gas'] = 'Positive (Margin Expansion)'
        impacts['Paints'] = 'Negative (Input Costs)'
        impacts['Aviation'] = 'Negative (Fuel Costs)'
        
    return impacts

def get_market_context():
    signals = get_macro_signals()
    regime = determine_regime(signals)
    impacts = get_sector_impacts(regime, signals)
    
    return {
        "regime": regime,
        "signals": signals,
        "impact_map": impacts,
        "timestamp": datetime.now().isoformat()
    }
    score = 0
    reasons = []
    
    # 1. Volatility
    if signals.get('vix', 0) > 15: 
        score += 1
        reasons.append(f"VIX Elevated ({signals['vix']})")

    # 2. Drawdown
    if signals.get('index_drawdown', 0) > 7: 
        score += 1
        reasons.append(f"Market Drawdown > 7% ({signals['index_drawdown']}%)")

    # 3. Interest Rates (Using Bond Yields as proxy if Rates stable)
    if signals.get('interest_rates_trend') == 'UP': 
        score += 1
        reasons.append("Interest Rates Rising")

    # 4. Bond Yields
    if signals.get('bond_yields_trend') == 'UP': 
        score += 1
        reasons.append("Bond Yields Rising")

    # 5. Commodity (Oil)
    if signals.get('oil_prices_trend') == 'UP': 
        score += 1
        reasons.append("Oil Prices Rising")
        
    # Classification
    if score <= 1: 
        regime = "NORMAL"
    elif score == 2: 
        regime = "ELEVATED_VOLATILITY"
    elif score == 3: 
        regime = "TIGHT_LIQUIDITY"
    else: 
        regime = "RISK_OFF"
        
    return regime, reasons

MACRO_SECTOR_MAP = {
    "INTEREST_RATES_UP": {
        "Banking": "Mixed (NIM impact vs Credit growth)",
        "Real Estate": "Negative (Higher mortgage rates)",
        "Infrastructure": "Negative (Higher cost of debt)", 
        "FMCG": "Mildly Negative"
    },
    "INFLATION_UP": {
        "FMCG": "Negative (Margin pressure)",
        "Energy": "Positive",
        "Metals": "Positive",
        "IT": "Neutral"
    },
    "OIL_UP": {
        "Aviation": "Negative (Fuel costs)",
        "Paints": "Negative (Raw material costs)",
        "FMCG": "Negative (Transport costs)",
        "Energy": "Positive"
    },
    "CURRENCY_WEAKNESS": {
        "IT Services": "Positive (Export earnings)",
        "Pharma": "Positive (Export earnings)",
        "Automobile": "Negative (Imported components)"
    }
}

def get_market_context():
    signals = get_macro_signals()
    regime, reasons = determine_regime(signals)
    
    # Simple logic to determine active impacts based on signals
    active_impacts = {}
    
    # If VIX is high, everything is stressed
    if signals.get('vix', 0) > 20:
         active_impacts["General"] = "High Volatility affects all beta assets"

    if signals.get('interest_rates_trend') == 'UP' or signals.get('bond_yields_trend') == 'UP':
        active_impacts.update(MACRO_SECTOR_MAP["INTEREST_RATES_UP"])
        
    if signals.get('oil_prices_trend') == 'UP':
        active_impacts.update(MACRO_SECTOR_MAP["OIL_UP"])
        
    # Default message if no specific major stress
    if not active_impacts and regime == "NORMAL":
        active_impacts = {"General": "Macro environment is stable."}

    return {
        "regime": regime,
        "score": 0, 
        "reasons": reasons,
        "signals": signals,
        "impact_map": active_impacts
    }
