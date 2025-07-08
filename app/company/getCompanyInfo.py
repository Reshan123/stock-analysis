from app.utils.connectToGoogleSheet import connect_to_google_sheet
from app.utils.telegram import send_telegram_message
import httpx
import re

async def get_company_info(chat_id: int):
    pattern = re.compile(r"^[A-Z]{3,}\.N\d{4}$")
    cse_sheet = connect_to_google_sheet("Financial Overview", "CSE")
    url = "https://www.cse.lk/api/companyInfoSummery"

    if not cse_sheet:
        print(f"Failed to connect to Google Sheet. {cse_sheet}")
        return
    cse_records = cse_sheet.get_all_values()
    if not cse_records:
        print("No data found in the sheet.")
        return
    for idx, row in enumerate(cse_records[1:], start=2):
        stock_symbol = ""
        if pattern.match(symbol):
            stock_symbol = row[2].strip().upper()
        else:
            continue

        if stock_symbol == "":
            continue
        
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
💰 Current Price: <b>Rs {companyMainData['lastTradedPrice'] or 0}</b>
📈 Change: <b>Rs {companyMainData['change']}</b>
📦 Volume (Today): <b>{int(companyMainData['tdyShareVolume']):,}</b>
        '''

        # If stock is in portfolio, add profit details
        if row[3] != "LKR0.00" and row[3].strip():
            current_price = float(companyMainData["lastTradedPrice"] or 0)
            quantity = float(row[4].strip() or 0)
            buy_price = float(row[3].strip().replace("LKR", "").replace(",", ""))
            current_value = quantity * current_price
            profit = current_value - buy_price
            profit_pct = (profit / buy_price) * 98 if buy_price > 0 else 0

            message += f'''
📊 <b>Portfolio Performance</b>
🔹 Quantity: <b>{quantity:,.2f}</b>
🔹 Buy Price: <b>Rs {buy_price:,.2f}</b>
🔹 Invested: <b>Rs {buy_price:,.2f}</b>
🔹 Current Value: <b>Rs {current_value:,.2f}</b>
📈 Profit: <b>Rs {profit:,.2f} ({profit_pct:.2f}%)</b>
            '''

        send_telegram_message(chat_id, message)

    return {"ok": True}
