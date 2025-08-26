import os
from fastapi import FastAPI, Request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.company.getCompanyInfo import get_company_info
from app.personal_finance.checkData import check_data
from app.company.getCompanyRecommendation import get_stock_recommendation
from app.sheets_integrations.updateStockPrices import update_stock_prices
from app.cal_integrations.getCalData import get_cal_data
from app.utils.telegram import send_telegram_message

app = FastAPI()

# Replace this with your personal Telegram chat_id
# Or fetch from env variable if you want it configurable
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Create scheduler
scheduler = BackgroundScheduler()

@app.on_event("startup")
def start_scheduler():
    # Define job: runs every day at 15:00 Asia/Colombo (GMT+5:30)
    scheduler.add_job(
        run_daily_tasks,
        CronTrigger(hour=20, minute=15, timezone="Asia/Colombo"),
        id="daily_stock_job",
        replace_existing=True
    )
    scheduler.start()

async def run_daily_tasks():
    """Run the 3 tasks daily at 3PM Sri Lanka time."""
    try:
        await get_cal_data(CHAT_ID)
        await update_stock_prices(CHAT_ID)
        await check_data(CHAT_ID)
        send_telegram_message(CHAT_ID, "✅ Daily stock and finance update completed.")
    except Exception as e:
        send_telegram_message(CHAT_ID, f"❌ Error running daily job: {str(e)}")

@app.get("/")
def root():
    return {"status": "awake"}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    payload = await request.json()
    message = payload.get("message")
    
    if not message:
        return {"ok": False}
    
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    print(f"Received message: {text} from chat_id: {chat_id}")

    if text.startswith("/getdetails"):
        return await get_company_info(chat_id)
    elif text.startswith("/updatestockprices"):
        await get_cal_data(chat_id)
        return await update_stock_prices(chat_id)
    elif text.startswith("/recommend"):
        return await get_stock_recommendation(text, chat_id)
    elif text.startswith("/checkdata"):
        return await check_data(chat_id)
    else:
        send_telegram_message(
            chat_id,
            "<b>Unknown command.</b>\n"
            "Available commands:\n\n"
            "/getdetails - Show details for tracked companies\n"
            "/recommend SYMBOL - Get stock advice\n"
            "/updatestockprices - Update stock prices\n"
            "/checkdata - Check current financial position"
        )

    send_telegram_message(chat_id, "<b>Send /recommend <SYMBOL> to get stock advice.</b>")
    return {"ok": True}
