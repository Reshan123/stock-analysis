from app.utils.connectToGoogleSheet import connect_to_google_sheet
from app.utils.telegram import send_telegram_message
import httpx

async def check_data(chat_id: str):
    net_worth = connect_to_google_sheet("Financial Overview", "Net Worth")

    if not net_worth:
        print(f"Failed to connect to Google Sheet. {net_worth}")
        return
    net_worth_records = net_worth.get_all_values()
    if not net_worth_records:
        print("No data found in the sheet.")
        return
    
    net_worth = 0
    for idx, row in enumerate(net_worth_records[1:], start=2):  # Skip header, start row index at 2
        if len(row) > 2 and row[1]:  # Check column B
            text = row[1].strip()
            if text == "Net Worth":
                net_worth = row[3]

    formatted = f"💰 <b>Net Worth:</b> ${netWorth}"
    print(f"Net worth: {formatted}")
    return {"ok": True}