from fastapi import FastAPI, Request
from app.company.getCompanyInfo import get_company_info
from app.personal_finance.checkData import check_data
from app.recommend import get_stock_recommendation
from app.sheets_integrations.updateStockPrices import update_stock_prices
from app.utils.telegram import send_telegram_message

app = FastAPI()

@app.get("/")
def root():
    return {"status": "awake"}

@app.post("/")
async def telegram_webhook(request: Request):
    payload = await request.json()
    print(f"Payload : {payload}" )
    if payload.message == "autoRun":
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        await update_stock_prices(chat_id)
        return await check_data(chat_id)
    
    message = payload.get("message")
    
    if not message:
        return {"ok": False}
    
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    print(f"Received message: {text} from chat_id: {chat_id}")

    if text.startswith("/getdetails"):
        return await get_company_info(chat_id)
    elif text.startswith("/updatestockprices"):
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
            "/checkdata - Check current finacial position"
        )

    send_telegram_message(chat_id, "<b>Send /recommend <SYMBOL> to get stock advice.</b>")
    return {"ok": True}
