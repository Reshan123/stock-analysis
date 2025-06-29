from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7673922428:AAFtLsVlehCWCPVpkGCVXbXPQDW-N4EtJ9U")
TELEGRAM_API_URL = f"https://api.telegram.org/bot7673922428:AAFtLsVlehCWCPVpkGCVXbXPQDW-N4EtJ9U"

def send_telegram_message(chat_id: int, text: str):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    payload = await request.json()
    
    message = payload.get("message")
    if not message:
        return {"ok": False}
    
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    print(f"Received message: {text} from chat_id: {chat_id}")

    # Example logic: if the user sends a stock symbol like "SAMP"
    if text.startswith("/getdetails"):
        f = open("companyList.txt")
        company_list = f.read().splitlines()
        for company in company_list:
            stock_symbol = company
        
            url = "https://www.cse.lk/api/companyInfoSummery"

            response = requests.post(url, data={"symbol": stock_symbol})
            if response.status_code != 200:
                send_telegram_message(chat_id, f'''<b>Invalid stock symbol: {stock_symbol}</b>''')
                return {"error": "Failed to fetch company information"}
            company_info = response.json()

            if company_info == {}:
                send_telegram_message(chat_id, f'''<b>Invalid stock symbol: {stock_symbol}</b>''')
                return {"ok": True}

            companyMainData = {
                "currentPrice": company_info['reqSymbolInfo']['lastTradedPrice'],
                "high": company_info['reqSymbolInfo']['allHiPrice'],
                "low": company_info['reqSymbolInfo']['allLowPrice'],
                "change": company_info['reqSymbolInfo']['change'],
                "name": company_info['reqSymbolInfo']['name'],
                "volume": company_info['reqSymbolInfo']['tdyShareVolume'],
                "closingPrice": company_info['reqSymbolInfo']['closingPrice'],
                "symbol": company_info['reqSymbolInfo']['symbol'],
                "hiTrade": company_info['reqSymbolInfo']['hiTrade'],
                "lowTrade": company_info['reqSymbolInfo']['lowTrade'],
            }

            price = companyMainData["currentPrice"]
            name = companyMainData["name"]
            volume = companyMainData["volume"]
            change = companyMainData["change"]
            closing = companyMainData["closingPrice"]
            symbol = companyMainData["symbol"]
            hiTrade = companyMainData["hiTrade"]
            lowTrade = companyMainData["lowTrade"]

            change_percent = round((change / (price - change)) * 100, 2) if price != 0 else 0.00

            
            message = f'''<b>{name} ({symbol})</b>
📉 Day Range: <b>Rs.{lowTrade} - Rs.{hiTrade}</b>
💰 Current Price: <b>Rs {price}</b>
📈 Change: <b>Rs {change}</b> (<i>{change_percent}%</i>)
📦 Volume (Today): <b>{volume:,}</b>'''

            send_telegram_message(chat_id, message)

        f.close()
    elif text.startswith("/add"):
        parts = text.split(" ")
        if len(parts) < 2 or not parts[1].strip():
            send_telegram_message(chat_id, "<b>Error: Please provide a company symbol. Usage: /add SYMBOL</b>")
        else:
            new_symbol = parts[1].strip().upper()
            with open("companyList.txt") as f:
                company_list = f.read().splitlines()
            if new_symbol not in company_list:
                with open("companyList.txt", "a") as file:
                    file.write(f"{new_symbol}\n")
                send_telegram_message(chat_id, f"<b>Added {new_symbol} to the company list.</b>")
            else:
                send_telegram_message(chat_id, f"<b>{new_symbol} is already in the company list.</b>")
    elif text.startswith("/remove"):
        parts = text.split(" ")
        if len(parts) < 2 or not parts[1].strip():
            send_telegram_message(chat_id, "<b>Error: Please provide a company symbol. Usage: /remove SYMBOL</b>")
        else:
            with open("companyList.txt", "r") as f:
                company_list = f.read().splitlines()

            symbol_to_remove = text.split(" ")[1].strip().upper()

            if symbol_to_remove in company_list:
                company_list.remove(symbol_to_remove)
                with open("companyList.txt", "w") as f:
                    f.write("\n".join(company_list) + "\n")
                send_telegram_message(chat_id, f'''<b>Removed {symbol_to_remove} from the company list.</b>''')
            else:
                send_telegram_message(chat_id, f'''<b>{symbol_to_remove} is not in the company list.</b>''')
    elif text.startswith("/getlist"):
        with open("companyList.txt", "r") as f:
            company_list = f.read().splitlines()
            if not company_list:
                send_telegram_message(chat_id, f'''<b>No companies in the list.</b>''')
            else:
                formatted_list = "\n".join([f"<code>{symbol}</code>" for symbol in company_list])
                send_telegram_message(chat_id, f'''<b>Company List:</b>\n{formatted_list}''')
    else:
        send_telegram_message(chat_id, f'''<b>Send /recommend <SYMBOL> to get stock advice.</b>''')

    return {"ok": True}
