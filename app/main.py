import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from fastapi import FastAPI, Depends, HTTPException, Security
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.company.getCompanyInfo import get_company_info
from app.personal_finance.checkData import check_data
from app.company.getCompanyRecommendation import get_stock_recommendation
from app.sheets_integrations.updateStockPrices import update_stock_prices
from app.data_pipeline.dataPipeline import data_pipeline
from app.cal_integrations.getCalData import get_cal_data
from app.utils.telegram import send_telegram_message
from app.web_api_endpoints.getBasicInfo import get_basic_info
from app.web_api_endpoints.getCseInfo import get_cse_info
from app.web_api_endpoints.getCseLiveData import get_cse_live_data

load_dotenv() 
app = FastAPI()

FRONTEND_ENDPOINT_URL = os.getenv("FRONTEND_ENDPOINT_URL", "<your_chat_id>")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "<your_chat_id>")
API_KEY = os.getenv("API_KEY")

origins = [
    FRONTEND_ENDPOINT_URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific origins
    allow_credentials=True, # Allows cookies to be included in requests
    allow_methods=["*"],    # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],    # Allows all headers
)

API_KEY_NAME = "X-API-Key"  # header name
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="Forbidden")

scheduler = BackgroundScheduler()
main_loop = None  # store reference to FastAPI's asyncio loop

# --- wrapper so APScheduler can run async tasks safely ---
def run_daily_tasks_wrapper():
    asyncio.run_coroutine_threadsafe(run_daily_tasks(), main_loop)

async def run_daily_tasks():
    """Run the 3 tasks daily at 3PM Sri Lanka time."""
    try:
        await get_cal_data(CHAT_ID, 2)
        await update_stock_prices(CHAT_ID, 2)
        await check_data(CHAT_ID, 2)
        print("✅ Daily stock and finance update completed.")
    except Exception as e:
        send_telegram_message(CHAT_ID, f"❌ Error running daily job: {str(e)}")
        print(f"❌ Error running daily job: {e}")

@app.on_event("startup")
async def start_scheduler():
    global main_loop
    main_loop = asyncio.get_event_loop()  # capture FastAPI's loop

    scheduler.add_job(
        run_daily_tasks_wrapper,
        CronTrigger(
            hour=15,
            minute=0,
            day_of_week="mon-fri",
            timezone="Asia/Colombo"
        ),
        id="daily_stock_job",
        replace_existing=True
    )
    scheduler.start()
    print("📅 Scheduler started. Daily job scheduled for 3PM Asia/Colombo (weekdays only).")

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
    elif text.startswith("/rundatapipeline"):
        return await data_pipeline(chat_id)
    else:
        send_telegram_message(
            chat_id,
            "<b>Unknown command.</b>\n"
            "Available commands:\n\n"
            "/getdetails - Show details for tracked companies\n"
            "/rundatapipeline - Update 'MyMoney Export' tab with current transactions\n"
            "/updatestockprices - Update stock prices\n"
            "/checkdata - Check current financial position"
        )

    send_telegram_message(chat_id, "<b>Send /recommend <SYMBOL> to get stock advice.</b>")
    return {"ok": True}
    
@app.post("/webhook_v2")
async def telegram_webhook(request: Request):
    payload = await request.json()
    message = payload.get("message")

    if not message:
        return {"ok": False}
    
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    print(f"Received message: {text} from chat_id: {chat_id}")

    if text.startswith("/getdetails"):
        return await get_company_info(chat_id, 2)
    elif text.startswith("/checkdata"):
        return await check_data(chat_id, 2)
    elif text.startswith("/updatestockprices"):
        await get_cal_data(chat_id, 2)
        return await update_stock_prices(chat_id, 2)
    elif text.startswith("/rundatapipeline"):
        return await data_pipeline(chat_id, 2)
    else:
        send_telegram_message(
            chat_id,
            "<b>Unknown command.</b>\n"
            "Available commands:\n\n"
            "/getdetails - Show details for tracked companies\n",
            2
        )
    return {"ok": True}

@app.head("/")
def root_head():
    return Response(status_code=200)

@app.get("/api/get_cse_info")
def getCseInfo(api_key: str = Depends(get_api_key)):
    return get_cse_info()

@app.get("/api/get_basic_info")
def getBasicInfo(api_key: str = Depends(get_api_key)):
    return get_basic_info()

@app.get("/api/get_cse_live_data")
def getBasicInfo(api_key: str = Depends(get_api_key)):
    return get_cse_live_data()