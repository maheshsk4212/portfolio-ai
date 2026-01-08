import os
from kiteconnect import KiteConnect
from sector_data import get_sector
from dotenv import load_dotenv

load_dotenv()

# Initialize KiteConnect
# Note: In a real/production scenario, you'd handle the full OAuth flow.
# For this MVP/personal tool, we assume the user might manually provide the access token
# or we use the API strictly with an existing session if possible, though Kite Connect
# requires a fresh login daily for the access token.
#
# We'll expose a helper to set the token.

kite = KiteConnect(api_key=os.getenv("KITE_API_KEY"))
TOKEN_FILE = "access_token.txt"

def load_token():
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as f:
                token = f.read().strip()
                if token:
                    kite.set_access_token(token)
                    print(f"Loaded access token from {TOKEN_FILE}")
    except Exception as e:
        print(f"Error loading token: {e}")

# Try loading on startup
load_token()

def set_access_token(token: str):
    """Sets the access token for the current session and saves it."""
    kite.set_access_token(token)
    try:
        with open(TOKEN_FILE, "w") as f:
            f.write(token)
    except Exception as e:
        print(f"Error saving token: {e}")

def get_portfolio_summary() -> dict:
    """
    Fetches positions/holdings and calculates summary.
    """
    # Check if KiteConnect is initialized and an access token is set
    # kite.access_token is set by set_access_token or generate_session
    if not kite or not getattr(kite, 'access_token', None):
        # Return EMPTY state if not logged in. No fake data.
        return {
            "total_value": 0.0,
            "sector_allocation": {},
            "holdings_count": 0,
            "unrealized_pnl": 0.0,
            "day_change": 0.0,
            "day_change_percentage": 0.0,
            "holdings": [],
            "data_source": "DISCONNECTED"
        }

    try:
        # Ideally fetch 'holdings' which are long term
        holdings = kite.holdings()
        
        total_value = 0.0
        total_unrealized_pnl = 0.0 # Renamed from 'pnl' to avoid confusion with individual stock pnl
        total_day_change = 0.0 # Renamed from 'day_change_total'
        sector_weights = {}
        processed_holdings = []

        for h in holdings:
            quantity = h['quantity']
            last_price = h['last_price']
            average_price = h['average_price']
            tradingsymbol = h['tradingsymbol']
            close_price = h.get('close_price', last_price) # Fallback if close_price is missing

            current_val = last_price * quantity
            stock_unrealized_pnl = h['pnl'] # Individual stock PnL
            stock_day_change = (last_price - close_price) * quantity
            stock_day_change_percentage = ((last_price - close_price) / close_price * 100) if close_price > 0 else 0.0

            total_value += current_val
            total_unrealized_pnl += stock_unrealized_pnl
            total_day_change += stock_day_change
            
            # Determine Sector
            sector = get_sector(tradingsymbol)
            sector_weights[sector] = sector_weights.get(sector, 0.0) + current_val
            
            processed_holdings.append({
                "tradingsymbol": tradingsymbol,
                "quantity": quantity,
                "last_price": last_price,
                "average_price": average_price,
                "pnl": round(stock_unrealized_pnl, 2),
                "day_change": round(stock_day_change, 2),
                "day_change_percentage": round(stock_day_change_percentage, 2),
                "value": round(current_val, 2),
                "sector": sector
            })

        sector_percent = {
            k: round((v / total_value) * 100, 2) if total_value > 0 else 0
            for k, v in sector_weights.items()
        }

        # Calculate overall day change percentage
        # The denominator should be the value at the start of the day (total_value - total_day_change)
        day_change_percentage = 0.0
        if (total_value - total_day_change) > 0:
            day_change_percentage = (total_day_change / (total_value - total_day_change)) * 100

        return {
            "total_value": round(total_value, 2),
            "sector_allocation": sector_percent,
            "holdings_count": len(holdings),
            "unrealized_pnl": round(total_unrealized_pnl, 2),
            "day_change": round(total_day_change, 2),
            "day_change_percentage": round(day_change_percentage, 2),
            "holdings": processed_holdings,
            "data_source": "LIVE"
        }

    except Exception as e:
        print(f"Error fetching holdings: {e}")
        return {
            "total_value": 0.0,
            "sector_allocation": {},
            "holdings_count": 0,
            "unrealized_pnl": 0.0,
            "day_change": 0.0,
            "day_change_percentage": 0.0,
            "holdings": []
        }

def get_login_url():
    return kite.login_url()

def generate_session(request_token: str):
    """
    Exchanges request_token for access_token.
    """
    try:
        data = kite.generate_session(request_token, api_secret=os.getenv("KITE_API_SECRET"))
        # Use our wrapper to save it
        set_access_token(data["access_token"])
        return data["access_token"]
    except Exception as e:
        print(f"Error generating session: {e}")
        return None
