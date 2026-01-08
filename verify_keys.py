import os
import openai
from kiteconnect import KiteConnect
from dotenv import load_dotenv

load_dotenv()

results = []

# 1. Check OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    results.append("❌ OpenAI API Key: MISSING from .env")
else:
    openai.api_key = api_key
    try:
        # Simple call to check auth
        openai.models.list()
        results.append("✅ OpenAI API Key: VALID")
    except Exception as e:
        results.append(f"❌ OpenAI API Key: INVALID\n   Error: {str(e)}")

# 2. Check Zerodha
kite_key = os.getenv("KITE_API_KEY")
kite_secret = os.getenv("KITE_API_SECRET")

if not kite_key:
    results.append("❌ Zerodha API Key: MISSING")
else:
    try:
        kite = KiteConnect(api_key=kite_key)
        login_url = kite.login_url()
        results.append(f"✅ Zerodha API Key: SEEMS VALID (Generated Login URL)")
        results.append(f"   Login URL: {login_url}")
    except Exception as e:
        results.append(f"❌ Zerodha API Key: INVALID\n   Error: {str(e)}")

# Save to file
with open("verify_result.txt", "w") as f:
    f.write("\n".join(results))

print("Verification complete.")
