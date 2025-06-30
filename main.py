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

            if not company_info or "reqSymbolInfo" not in company_info or not company_info["reqSymbolInfo"].get("lastTradedPrice"):
                send_telegram_message(chat_id, (
                    f"📡 <b>Market data for {stock_symbol} is currently unavailable.</b>\n"
                    f"🕖 This typically occurs before the Colombo Stock Exchange opens.\n"
                    f"⏰ Please try again after <b>9:30 AM</b>."
                ))
                return {"error": "Market data unavailable"}

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
            if not company_info or "reqSymbolInfo" not in company_info or not company_info["reqSymbolInfo"].get("lastTradedPrice"):
                send_telegram_message(chat_id, (
                    f"📡 <b>Market data for {symbol} is currently unavailable.</b>\n"
                    f"🕖 This typically occurs before the Colombo Stock Exchange opens.\n"
                    f"⏰ Please try again after <b>9:30 AM</b>."
                ))
                return {"error": "Market data unavailable"}

            info = company_info["reqSymbolInfo"]
            prompt = f"""
        You are a professional stock market advisor AI with expertise in analyzing Sri Lankan equities. Analyze the following real-time stock data for <b>{info['name']} ({info['symbol']})</b> and provide a concise investment recommendation.

<b>Requirements:</b>
- Use proper <b>HTML formatting</b> (no Markdown).
- Use bullet points with • for readability.
- Use <b>bold</b> tags to emphasize key terms or labels.
- Use <i>italics</i> where appropriate (e.g., when noting uncertainty or caution).
- Keep it short, factual, and actionable (max 7 bullet points).
- If unusual volatility or market behavior is detected, include a note about it.
- Do not invent news — rely only on visible data or widely known context about the company or sector.

<b>Stock Data:</b><br>
• Company: <b>{info['name']} ({info['symbol']})</b><br>
• Current Price: <b>{info['lastTradedPrice']} LKR</b><br>
• Day High: <b>{info['hiTrade']} LKR</b><br>
• Day Low: <b>{info['lowTrade']} LKR</b><br>
• Change Today: <b>{info['change']} LKR</b><br>
• Previous Close: <b>{info['closingPrice']} LKR</b><br>

<b>Output Format:</b><br>
Begin with a heading like: <b>Investment Recommendation for {info['name']} ({info['symbol']})</b><br>
Then provide 5 to 7 bullet points based on the analysis, followed by a brief summary sentence.
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
