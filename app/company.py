import httpx
from app.telegram import send_telegram_message
import os
from pathlib import Path
import json

async def get_company_info(chat_id: int):
    # Load portfolio data if available
    portfolio_file = Path(__file__).resolve().parent / "portfolio.json"
    portfolio = {}
    if portfolio_file.exists():
        with open(portfolio_file) as f:
            portfolio = json.load(f)
    # Load the company list
    company_list_file = Path(__file__).resolve().parent / "companyList.txt"
    with open(company_list_file) as f:
        company_list = f.read().splitlines()

    for stock_symbol in company_list:
        url = "https://www.cse.lk/api/companyInfoSummery"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data={"symbol": stock_symbol})

        if response.status_code != 200:
            send_telegram_message(chat_id, f"<b>Invalid stock symbol: {stock_symbol}</b>")
            continue

        company_info = response.json()
        if not company_info or "reqSymbolInfo" not in company_info:
            send_telegram_message(chat_id, f"<b>Invalid stock symbol: {stock_symbol}</b>")
            continue

        companyMainData = company_info["reqSymbolInfo"]

        # Base message (always shown)
        message = f'''
<b>{companyMainData['name']} ({stock_symbol})</b>
📉 Day Range: <b>Rs.{companyMainData['lowTrade']} - Rs.{companyMainData['hiTrade']}</b>
💰 Previous Close: <b>Rs {companyMainData['previousClose']}</b>
💰 Current Price: <b>Rs {companyMainData['lastTradedPrice']}</b>
📈 Change: <b>Rs {companyMainData['change']}</b>
📦 Volume (Today): <b>{int(companyMainData['tdyShareVolume']):,}</b>
        '''

        # If stock is in portfolio, add profit details
        if stock_symbol in portfolio:
            data = portfolio[stock_symbol]
            current_price = float(companyMainData["lastTradedPrice"])
            quantity = data["quantity"]
            buy_price = data["buy_price"]
            invested = quantity * buy_price
            current_value = quantity * current_price
            profit = current_value - invested
            profit_pct = (profit / invested) * 98 if invested > 0 else 0

            message += f'''
📊 <b>Portfolio Performance</b>
🔹 Quantity: <b>{quantity}</b>
🔹 Buy Price: <b>Rs {buy_price}</b>
🔹 Invested: <b>Rs {invested:,.2f}</b>
🔹 Current Value: <b>Rs {current_value:,.2f}</b>
📈 Profit: <b>Rs {profit:,.2f} ({profit_pct:.2f}%)</b>
            '''

        send_telegram_message(chat_id, message)

    return {"ok": True}


async def manage_company_list(text: str, chat_id: int):
    parts = text.split(" ")
    if len(parts) < 2 or not parts[1].strip():
        send_telegram_message(chat_id, "<b>Error: Please provide a company symbol. Usage: /add SYMBOL</b>")
    else:
        command = parts[0].lower()
        symbol = parts[1].strip().upper()
        file_path = Path(__file__).resolve().parent / "companyList.txt"
        cse_api_url = "https://www.cse.lk/api/companyInfoSummery"

        # Read the current list
        if not os.path.exists(file_path):
            open(file_path, "w").close()  # create empty file if not exists

        with open(file_path, "r") as f:
            company_list = f.read().splitlines()

        if command == "/add":

            # Validate symbol with API
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(cse_api_url, data={"symbol": symbol})
            
            if response.status_code != 200:
                send_telegram_message(chat_id, f"<b>❌ Failed to validate symbol {symbol}. Try again later.</b>")
                return {"error": "API validation failed"}

            data = response.json()
            if not data or "reqSymbolInfo" not in data or not data["reqSymbolInfo"].get("lastTradedPrice"):
                send_telegram_message(chat_id, f"<b>⚠️ {symbol} is not a valid stock symbol on the CSE.</b>")
                return {"error": "Invalid stock symbol"}

            # Add if valid and not already in list
            if symbol not in company_list:
                with open(file_path, "a") as f:
                    f.write(f"{symbol}\n")
                send_telegram_message(chat_id, f"<b>✅ Added {symbol} to the company list.</b>")
            else:
                send_telegram_message(chat_id, f"<b>ℹ️ {symbol} is already in the company list.</b>")

        elif command == "/remove":
            if symbol in company_list:
                company_list.remove(symbol)
                with open(file_path, "w") as f:
                    f.write("\n".join(company_list) + "\n" if company_list else "")
                send_telegram_message(chat_id, f"<b>🗑️ Removed {symbol} from the company list.</b>")
            else:
                send_telegram_message(chat_id, f"<b>⚠️ {symbol} is not in the company list.</b>")
        else:
            send_telegram_message(chat_id, "<b>Unknown operation. Use /add or /remove followed by a stock symbol.</b>")

        return {"ok": True}

        

async def get_company_list(chat_id: int):
    try:
        file_path = Path(__file__).resolve().parent / "companyList.txt"
        with open(file_path, "r") as f:
            company_list = f.read().splitlines()

        if not company_list:
            send_telegram_message(chat_id, "<b>No companies in the list.</b>")
        else:
            formatted_list = "\n".join([f"<code>{symbol}</code>" for symbol in company_list])
            send_telegram_message(chat_id, f"<b>Company List:</b>\n{formatted_list}")

        return {"ok": True}
    except FileNotFoundError:
        send_telegram_message(chat_id, "<b>Error:</b> company list file not found.")
        return {"error": "File not found"}