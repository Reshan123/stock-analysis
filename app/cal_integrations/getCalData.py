import requests
import os

from app.utils.connectToGoogleSheet import connect_to_google_sheet
from app.utils.telegram import send_telegram_message

async def get_cal_data(chat_id: int, bot_version = 1):
    try:
        payload = os.getenv("CAL_AUTH_PAYLOAD")

        cal_auth_token = os.getenv("CAL_AUTH_TOKEN")
        tokenResponse = requests.post("https://portal.cal.lk/oauth/token", data=payload, headers={
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "authorization": f"Basic {cal_auth_token}"
        })

        tokenResponse = tokenResponse.json()
        accessToken = tokenResponse["access_token"]

        calData = requests.get("https://portal.cal.lk/api/v1/account/me/financial/balances", headers={
            "authorization": f"Bearer {accessToken}",
            "Content-Type": "application/json"
        })

        calData = calData.json()
        calUnitsTotal = calData["total"]
        print(f"Cal Data: {calUnitsTotal}")

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
        if bot_version == 1         :
            send_telegram_message(
                chat_id=chat_id,  # Replace with your actual chat ID
                text=f"<b>✅ Unit Trust Values Updated Successfully</b>",
                bot_version=bot_version
            )    

    except Exception as e:
        print(f"Error in get_cal_data: {e}")
        send_telegram_message(
            chat_id=chat_id,  # Replace with your actual chat ID
            text=f"<b>Error updating Unit Trust prices: {e}</b>",
            bot_version=bot_version
        )
