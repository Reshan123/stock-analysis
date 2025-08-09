import requests
import os

from app.utils.connectToGoogleSheet import connect_to_google_sheet
from app.utils.telegram import send_telegram_message

async def get_cal_data(chat_id: int):
    payload = "username=200235800042&password=f4f8fd7d2eecb324f94a813a6fbc12f5a222ef8e5c99b8feab01a3379ec8f362eQJ4SehgroebHxcchN4uIA%3D%3D&captchaResponse=undefined%2C&captchaAttempts=1&grant_type=password&scope=trust"

    tokenResponse = requests.post("https://portal.cal.lk/oauth/token", data=payload, headers={
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "authorization": "Basic c0o2Zk9hdlhoZE1jYU1UaEVDVks6Z01WNFUybURhNHNIcDl1MUIzMjRibXJVUHZRWGZYU0Z6NGNuOVo2MVVlUTlRdUpSSGE="
    })

    tokenResponse = tokenResponse.json()
    # {'access_token': 'f0f7a756-2820-4258-9a18-db9370870fc3', 'token_type': 'bearer', 'refresh_token': 'ca6fb940-d26e-41a2-9b2d-c9054d7ed224', 'expires_in': 1622, 'scope': 'trust'}
    accessToken = tokenResponse["access_token"]

    calData = requests.get("https://portal.cal.lk/api/v1/account/me/financial/balances", headers={
        "authorization": f"Bearer {accessToken}",
        "Content-Type": "application/json"
    })

    calData = calData.json()
    calUnitsTotal = calData["total"]
    print(f"Cal Data: {calUnitsTotal}")
    # {'balances': [{'crmId': '3e64e4d1-80c7-ef11-a72f-000d3a80655d', 'balance': 53510.36, 'formattedBalance': '53,510.36', 'division': 'UNIT_TRUST', 'accountType': 'INDIVIDUAL', 'accountName': 'Mr. Gomis', 'utTransactionsEnabled': True, 'pwmValuationDate': None, 'clientCode': 'ILG0595'}], 'total': 53510.36, 'totalNonCorporateBalance': 53510.36, 'productWiseBalance': {'CALI': {'TOTAL': '53,510.36', 'JOINT': '', 'CORPORATE': '', 'INDIVIDUAL': '53,510.36'}}, 'products': ['CALI']}

    net_worth_sheet = connect_to_google_sheet("Financial Overview", "Net Worth")
    if not net_worth_sheet:
        print(f"Failed to connect to Google Sheet. {net_worth_sheet}")
        return
    net_worth_records = net_worth_sheet.get_all_values()

    for idx, row in enumerate(net_worth_records[1:], start=2):  # Skip header, start row index at 2
        if len(row) > 2 and row[1]:  # Check column B
            text = row[1].strip()
            if text == "Unit Trust":
                net_worth_sheet.update_cell(idx, 4, calUnitsTotal)  # Column E = index 5
                print(f"Updated row {idx} with value '{calUnitsTotal}' for Unit Trust")
    send_telegram_message(
        chat_id=chat_id,  # Replace with your actual chat ID
        text=f"<b>Unit prices updated successfully in 'Financial Overview' sheet.</b>"
    )
