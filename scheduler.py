from apscheduler.schedulers.background import BackgroundScheduler
from zerodha import get_portfolio_summary
from ai_brain import analyze_portfolio
import datetime

scheduler = BackgroundScheduler()

def daily_job():
    print(f"[{datetime.datetime.now()}] Running Daily Portfolio Analysis...")
    try:
        portfolio = get_portfolio_summary()
        # In a real app, we would save this insight to the database.
        # For now, we just print it to demonstrate the flow.
        insight = analyze_portfolio(portfolio)
        print("DAILY AI INSIGHT GENERATED:")
        print(insight.get("analysis", "No analysis generated."))
    except Exception as e:
        print(f"Error in daily job: {e}")

def start_scheduler():
    # schedule for 9:20 AM daily
    scheduler.add_job(daily_job, "cron", hour=9, minute=20)
    scheduler.start()
    print("Scheduler started. Daily analysis set for 09:20 AM.")
