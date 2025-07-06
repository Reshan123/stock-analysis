import httpx
from app.utils.telegram import send_telegram_message
import os
from pathlib import Path

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
