# Static Sector Mapping for Indian Stocks
# This is a helper file to enrich portfolio data.

SECTOR_MAP = {
    # IT Services
    "TCS": "IT Services",
    "INFY": "IT Services",
    "HCLTECH": "IT Services",
    "WIPRO": "IT Services",
    "TECHM": "IT Services",
    "LTIM": "IT Services",
    "TATATECH": "IT Services",
    
    # Banks - Private
    "HDFCBANK": "Banking",
    "ICICIBANK": "Banking",
    "KOTAKBANK": "Banking",
    "AXISBANK": "Banking",
    "INDUSINDBK": "Banking",
    "CUB": "Banking",
    "IDFCFIRSTB": "Banking",
    
    # Banks - PSU
    "SBIN": "Banking",
    "PNB": "Banking",
    "BANKBARODA": "Banking",
    
    # Finance & NBFC
    "BAJFINANCE": "Finance",
    "BAJAJFINSV": "Finance",
    "SBILIFE": "Insurance",
    "HDFCLIFE": "Insurance",
    "ARMANFIN": "Finance",
    "SBICARD": "Finance",
    "JIOFIN": "Finance",
    "IREDA": "Finance",
    
    # Oil, Gas & Energy
    "RELIANCE": "Energy",
    "ONGC": "Energy",
    "BPCL": "Energy",
    "IOC": "Energy",
    "POWERGRID": "Power",
    "NTPC": "Power",
    "ADANIGREEN": "Power",
    
    # FMCG
    "HINDUNILVR": "FMCG",
    "ITC": "FMCG",
    "NESTLEIND": "FMCG",
    "BRITANNIA": "FMCG",
    "TATACONSUM": "FMCG",
    "DABUR": "FMCG",
    
    # Auto
    "MARUTI": "Automobile",
    "TATAMOTORS": "Automobile",
    "M&M": "Automobile",
    "BAJAJ-AUTO": "Automobile",
    "EICHERMOT": "Automobile",
    "HEROMOTOCO": "Automobile",
    
    # Metals & Mining
    "TATASTEEL": "Metals",
    "HINDALCO": "Metals",
    "JSWSTEEL": "Metals",
    "COALINDIA": "Mining",
    
    # Infra & Construction
    "LT": "Construction",
    "ULTRACEMCO": "Cement",
    "ADANIENT": "Diversified",
    "ADANIPORTS": "Infrastructure",
    "CGPOWER": "Engineering",
    
    # Pharma
    "SUNPHARMA": "Pharma",
    "DRREDDY": "Pharma",
    "CIPLA": "Pharma",
    "DIVISLAB": "Pharma",
    
    # Telecom
    "BHARTIARTL": "Telecom",
    "TATACOMM": "Telecom",
    
    # Consumer Discretionary
    "TITAN": "Consumer Durables",
    "ASIANPAINT": "Paints",
    "INDIGOPNTS": "Paints",
    "PVRINOX": "Media & Entertainment",

    # ETFs & Funds
    "NIFTYBEES": "ETF",
    "ITBEES": "ETF",
    "MID150BEES": "ETF",
    "SENSEXBEES": "ETF",
    "LIQUIDCASE": "Liquid Fund",
}

def get_sector(symbol: str) -> str:
    """Returns the sector for a given symbol, or 'Other' if unknown."""
    # Handle cases like 'TCS-EQ' or just 'TCS'
    clean_symbol = symbol.split('-')[0]
    return SECTOR_MAP.get(clean_symbol, "Other")
