from fastapi import FastAPI, Request
from app.recommend import get_stock_recommendation
from app.telegram import send_telegram_message, markdown_to_telegram_html, clean_telegram_html
from app.company import get_company_info, get_company_list, manage_company_list
import os

app = FastAPI()

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
    elif text.startswith("/add") or text.startswith("/remove"):
        return await manage_company_list(text, chat_id)
    elif text.startswith("/getlist"):
        return await get_company_list(chat_id)
    elif text.startswith("/recommend"):
        return await get_stock_recommendation(text, chat_id)
    else:
        send_telegram_message(chat_id, "<b>Unknown command.</b>\nTry one of the following:\n"
                                   "/getlist - List tracked companies\n"
                                   "/add SYMBOL - Add a stock symbol\n"
                                   "/remove SYMBOL - Remove a stock symbol\n"
                                   "/getdetails - Show details for tracked companies\n"
                                   "/recommend SYMBOL - Get an investment suggestion")

    send_telegram_message(chat_id, "<b>Send /recommend <SYMBOL> to get stock advice.</b>")
    return {"ok": True}
