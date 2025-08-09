from app.utils.connectToGoogleSheet import connect_to_google_sheet
from app.utils.telegram import send_telegram_message
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import httpx

async def check_data(chat_id: int):
    net_worth_sheet = connect_to_google_sheet("Financial Overview", "Net Worth")

    if not net_worth_sheet:
        print(f"Failed to connect to Google Sheet. {net_worth_sheet}")
        return
    net_worth_records = net_worth_sheet.get_all_values()
    if not net_worth_records:
        print("No data found in the sheet.")
        return
    
    net_worth = 0
    my_cse_balance = 0
    my_unit_trust_balance = 0
    dad_cse_balance = 0
    for idx, row in enumerate(net_worth_records[1:], start=2):  # Skip header, start row index at 2
        if len(row) > 2 and row[1]:  # Check column B
            text = row[1].strip()
            if text == "Net Worth":
                net_worth = row[3]
            elif text == "Thaththi CSE":
                dad_cse_balance = row[4]
            elif text == "CSE":
                my_cse_balance = row[3]
            elif text == "Unit Trust":
                my_unit_trust_balance = row[3]


    formatted_net_worth = f"💰 <b>Net Worth:</b> {net_worth}"
    formatted_dad_cse_balance = f"👨‍👦 <b>Dad's CSE Balance:</b> LKR{dad_cse_balance}" if 'dad_cse_balance' in locals() else ""
    formatted_my_unit_trust_balance = f"👤 <b>My Unit Trust Balance:</b> {my_unit_trust_balance}" if my_unit_trust_balance in locals() else ""
    formatted_my_cse_balance = f"👤 <b>My CSE Balance:</b> {my_cse_balance}" if my_cse_balance in locals() else ""

    my_money_export_sheet = connect_to_google_sheet("Financial Overview", "My Money Export")
    if not my_money_export_sheet:
        print(f"Failed to connect to Google Sheet. {my_money_export_sheet}")
        return
    my_money_export_records = my_money_export_sheet.get_all_values()
    if not my_money_export_records:
        print("No data found in the sheet.")
        return
    
    last_date = datetime.strptime(my_money_export_records[-1][0], "%m/%d/%Y")
    check_date = datetime.today() - timedelta(days=5)

    message = ""
    if check_date > last_date:
        message = (
            "⚠️ <b>Action Required</b>\n\n"
            "Your <i>Money Export Sheet</i> appears to be outdated.\n\n"
            f"📅 Last entry: <b>{last_date.strftime('%a %b %d %Y')}</b>\n"
            "🕒 Please update your <i>Financial Overview</i> now."
        )
    else:
        message = (
            "✅ <b>All Good!</b>\n\n"
            "Your <i>Money Export Sheet</i> is up to date.\n\n"
            f"📅 Last entry: <b>{last_date.strftime('%a %b %d %Y')}</b>\n"
            "⏳ Next check will be in a week."
        )

    message += f"\n\n{formatted_net_worth}"
    message += f"\n\n{formatted_my_cse_balance}"
    message += f"\n\n{formatted_my_unit_trust_balance}"
    message += f"\n\n{formatted_dad_cse_balance}"
    message += "\n----------------------------------------------------------------\n"

    today = datetime.today()
    is_after_24th = today.day >= 25
    target_date = today + relativedelta(months=1) if is_after_24th else today
    monthly_sheet_name = target_date.strftime('%B')

    monthly_sheet = connect_to_google_sheet("Salary Breakdown", work_sheet_name=monthly_sheet_name)
    if not monthly_sheet:
        print(f"Failed to connect to Google Sheet. {monthly_sheet}")
        return
    monthly_sheet_records = monthly_sheet.get_all_values()
    if not monthly_sheet_records:
        print("No data found in the sheet.")
        return
    # Filter for rows where the second column is "FALSE"
    pending_transactions = [row for row in monthly_sheet_records if row[1] == "FALSE"]

    # Create message
    if pending_transactions:
        items = "\n".join(
            f"🔸 {row[0] if row[0] else 'Unnamed Transaction'} | {row[2] if len(row) > 2 and row[2] else '0.00'}"
            for row in pending_transactions
        )
        message += (
            "⚠️ <b>Pending Transactions</b>\n\n"
            "The following transactions are still incomplete:\n\n"
            f"{items}\n\n"
            "📌 Please review and update them."
        )
    else:
        message += (
            "✅ <b>All Transactions Completed</b>\n\n"
            "Everything in your monthly sheet is marked as done. Great job!"
        )

    send_telegram_message(
        chat_id=chat_id,  # Replace with your actual chat ID
        text=message
    )  
    
    return {"ok": True}