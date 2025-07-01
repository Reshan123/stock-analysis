import httpx
from app.telegram import send_telegram_message
import os
from pathlib import Path

async def get_company_info(chat_id: int):
    # Opening the file asynchronously might be a better choice for performance,
    # though it's not strictly necessary for small file sizes
    file_path = Path(__file__).resolve().parent / "companyList.txt"
    with open(file_path) as f:
        company_list = f.read().splitlines()

    for company in company_list:
        stock_symbol = company
        url = "https://www.cse.lk/api/companyInfoSummery"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, data={"symbol": stock_symbol})

        if response.status_code != 200:
            send_telegram_message(chat_id, f"<b>Invalid stock symbol: {stock_symbol}</b>")
            return {"error": "Failed to fetch company information"}

        company_info = response.json()
        if not company_info or "reqSymbolInfo" not in company_info:
            send_telegram_message(chat_id, f"<b>Invalid stock symbol: {stock_symbol}</b>")
            return {"ok": True}

        companyMainData = company_info['reqSymbolInfo']
        message = f'''
        <b>{companyMainData['name']} ({companyMainData['symbol']})</b>
📉 Day Range: <b>Rs.{companyMainData['lowTrade']} - Rs.{companyMainData['hiTrade']}</b>
💰 Previous Close Price: <b>Rs {companyMainData['closingPrice']}</b>
💰 Current Price: <b>Rs {companyMainData['lastTradedPrice']}</b>
📈 Change: <b>Rs {companyMainData['change']}</b>
📦 Volume (Today): <b>{companyMainData['tdyShareVolume']:,}</b>
        '''
        send_telegram_message(chat_id, message)

    return {"ok": True}

async def manage_company_list(text: str, chat_id: int):
    parts = text.split(" ")
    if len(parts) < 2 or not parts[1].strip():
        send_telegram_message(chat_id, "<b>Error: Please provide a company symbol. Usage: /add SYMBOL</b>")
    else:
        # Logic to add or remove from the list
        pass
