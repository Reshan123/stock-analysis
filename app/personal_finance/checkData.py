from app.utils.connectToGoogleSheet import connect_to_google_sheet
from app.utils.telegram import send_telegram_message
import httpx
from datetime import datetime

async def check_data(chat_id: str):
    net_worth_sheet = connect_to_google_sheet("Financial Overview", "Net Worth")

    if not net_worth_sheet:
        print(f"Failed to connect to Google Sheet. {net_worth_sheet}")
        return
    net_worth_records = net_worth_sheet.get_all_values()
    if not net_worth_records:
        print("No data found in the sheet.")
        return
    
    net_worth = 0
    for idx, row in enumerate(net_worth_records[1:], start=2):  # Skip header, start row index at 2
        if len(row) > 2 and row[1]:  # Check column B
            text = row[1].strip()
            if text == "Net Worth":
                net_worth = row[3]

    formatted = f"💰 <b>Net Worth:</b> ${net_worth}"

    my_money_export_sheet = connect_to_google_sheet("Financial Overview", "My Money Export")
    if not my_money_export_sheet:
        print(f"Failed to connect to Google Sheet. {my_money_export_sheet}")
        return
    my_money_export_records = my_money_export_sheet.get_all_values()
    if not my_money_export_records:
        print("No data found in the sheet.")
        return
    
    last_date = datetime.strptime(my_money_export_records[-1][0], "%m/%d/%Y")
    print(f"last date: {last_date}")
    
    

    
    return {"ok": True}