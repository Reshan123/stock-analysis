
from app.web_api_endpoints.getCseInfo import get_cse_info
import httpx

def get_cse_live_data():
    url = "https://www.cse.lk/api/companyInfoSummery"

    companies = get_cse_info().get("companies", [])

    for company in companies:
        stock_symbol = company["stock_symbol"]
        actual_cost = company["actual_cost"]
        current_value = company["current_value"]
        number_of_shares = company["number_of_shares"]

        if actual_cost == "LKR0.00" or actual_cost == "":
            actual_cost_value = 0
        else:
            actual_cost_value = float(actual_cost.replace("LKR", "").replace(",", ""))

        if current_value == "LKR0.00" or current_value == "":
            current_cost_value = 0
        else:
            current_cost_value = float(current_value.replace("LKR", "").replace(",", ""))

        print(f"Current Cost Value: {current_cost_value}, Actual Cost Value: {current_value}")
        if number_of_shares == "":
            quantity = 0
        else:
            quantity = float(number_of_shares.replace(",", ""))

        if stock_symbol == "":
            continue

        async def fetch_company_data(symbol):
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data={"symbol": symbol})
                if response.status_code == 200:
                    return response.json()
                else:
                    return None

        import asyncio
        company_info = asyncio.run(fetch_company_data(stock_symbol))

        if not company_info or "reqSymbolInfo" not in company_info:
            continue

        companyMainData = company_info["reqSymbolInfo"]
        current_price = float(companyMainData["lastTradedPrice"] or 0)
        gain_loss = current_cost_value - actual_cost_value

        company.update({
            "company_name": companyMainData['name'],
            "day_range": f"Rs.{companyMainData['lowTrade']} - Rs.{companyMainData['hiTrade']}",
            "previous_close": f"Rs {companyMainData['previousClose']}",
            "current_price": f"Rs {companyMainData['lastTradedPrice'] or 0}",
            "change": f"Rs {companyMainData['change']}",
            "volume_today": f"{int(companyMainData['tdyShareVolume']):,}",
            "current_price_value": current_price,
            "current_value": f"LKR{current_cost_value:,.2f}",
            "gain_loss": f"LKR{gain_loss:,.2f}",
            "gain_loss_value": gain_loss,
        })
        
    return companies;