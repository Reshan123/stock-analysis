import json
from pathlib import Path
import httpx
from app.utils.telegram import send_telegram_message


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
💰 Current Price: <b>Rs {companyMainData['lastTradedPrice'] or 0}</b>
📈 Change: <b>Rs {companyMainData['change']}</b>
📦 Volume (Today): <b>{int(companyMainData['tdyShareVolume']):,}</b>
        '''

        # If stock is in portfolio, add profit details
        if stock_symbol in portfolio:
            data = portfolio[stock_symbol]
            current_price = float(companyMainData["lastTradedPrice"] or 0)
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
