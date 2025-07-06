import re

import httpx
from app.utils.connectToGoogleSheet import connect_to_google_sheet


async def update_stock_prices():
    sheet_name = "Financial Overview"
    sheet = connect_to_google_sheet(sheet_name)
    print(f"Connected to Google Sheet: {sheet_name}")
    if not sheet:
        print("Failed to connect to Google Sheet.")
        return
    records = sheet.get_all_values()
    if not records:
        print("No data found in the sheet.")
        return
    
    CODE_REGEX = re.compile(r"^[A-Z]{3,4}\.[A-Z]\d{3,4}$")
    cse_api_url = "https://www.cse.lk/api/companyInfoSummery"
    
    for idx, row in enumerate(records[1:], start=2):  # Skip header, start row index at 2
        if len(row) > 2 and row[2]:  # Check column C
            code = row[2].strip()
            if not CODE_REGEX.match(code):
                print(f"Skipping invalid code format: {code}")
                continue  # Skip invalid formats
            else:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(cse_api_url, data={"symbol": code})
            
                if response.status_code != 200:
                    print(f"Failed to fetch data for code: {code}, status code: {response.status_code}")
                    continue

                data = response.json()
                if not data or "reqSymbolInfo" not in data or not data["reqSymbolInfo"].get("lastTradedPrice"):
                    print(f"Invalid stock symbol: {code}")
                    continue  # Skip invalid stock symbols
                sheet.update_cell(idx, 5, data.reqSymbolInfo.previousClose)  # Column E = index 5
                print(f"Updated row {idx} with value '{data.reqSymbolInfo.previousClose}' for code '{code}'")