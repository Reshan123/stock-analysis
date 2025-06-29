from fastapi import FastAPI, Request
import requests
import os
import httpx
import re

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_telegram_message(chat_id: int, text: str):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

def markdown_to_telegram_html(markdown_text: str) -> str:
    # Remove <think> tags
    markdown_text = re.sub(r"</?think>", "", markdown_text).strip()

    # Add line breaks
    markdown_text = markdown_text.replace("\n", "<br>")

    return markdown_text

def clean_telegram_html(text):
    # Remove any invalid HTML tags
    allowed_tags = ["b", "i", "u", "s", "code", "pre", "a"]
    # Replace <think> or anything not allowed
    return re.sub(r"</?(?!(" + "|".join(allowed_tags) + r"))[^>]+>", "", text)

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
    elif text.startswith("/recommend"):
        parts = text.split(" ")
        if len(parts) < 2 or not parts[1].strip():
            send_telegram_message(chat_id, "<b>Error: Please provide a company symbol. Usage: /add SYMBOL</b>")
        else:
            symbol = text.split(" ")[1].strip().upper()
            url = "https://www.cse.lk/api/companyInfoSummery"
            
            response = requests.post(url, data={"symbol": symbol})
            if response.status_code != 200:
                send_telegram_message(chat_id, f'''<b>Invalid stock symbol: {symbol}</b>''')
                return {"error": "Failed to fetch company information"}

            company_info = response.json()
            if not company_info or "reqSymbolInfo" not in company_info:
                send_telegram_message(chat_id, f'''<b>Invalid stock symbol: {symbol}</b>''')
                return {"error": "Invalid company data"}

            info = company_info["reqSymbolInfo"]
            prompt = f"""
        You are a stock market advisor AI. Analyze the following company information and give a short investment recommendation in bullet points.

        Please return the output using proper HTML formatting with <b>, <i>, and bullet points using • (not raw Markdown).

        Company: {info['name']} ({info['symbol']})
        Current Price: {info['lastTradedPrice']} LKR
        Day High: {info['hiTrade']} LKR
        Day Low: {info['lowTrade']} LKR
        Change Today: {info['change']} LKR
        Previous Close: {info['closingPrice']} LKR

        ### Recommendation:
        """

            together_payload = {
                "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
                "messages": [{"role": "user", "content": prompt}]
            }

            headers = {
                "Authorization": f"Bearer {os.getenv('TOGETHER_AI_API_KEY', '')}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                together_response = await client.post(
                    "https://api.together.xyz/v1/chat/completions",
                    headers=headers,
                    json=together_payload
                )

            if together_response.status_code != 200:
                return {"error": "AI generation failed", "details": together_response.text}

            result = together_response.json()
            reply = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            reply_cleaned = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL)
            send_telegram_message(chat_id, reply_cleaned)

    else:
        send_telegram_message(chat_id, f'''<b>Send /recommend <SYMBOL> to get stock advice.</b>''')

    return {"ok": True}
