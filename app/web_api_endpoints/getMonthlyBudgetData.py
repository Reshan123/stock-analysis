from app.utils.connectToGoogleSheet import connect_to_google_sheet
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

def get_monthly_budget_data():
    today = datetime.today()
    is_after_24th = today.day >= 25
    target_date = today + relativedelta(months=1) if is_after_24th else today
    monthly_sheet_name = target_date.strftime('%B')

    monthly_sheet = connect_to_google_sheet("Salary Breakdown", work_sheet_name=monthly_sheet_name)
    if not monthly_sheet:
        print(f"Failed to connect to Google Sheet. {monthly_sheet}")
        return {"error": "Failed to connect to Google Sheet."}
    
    records = monthly_sheet.get_all_values()
    if not records or len(records) < 2:
        print("No data found in the sheet.")
        return {"error": "No data found in the sheet."}
    
    headers = records[0]
    data = []
    for row in records[2:]:
        if row[0] == "Remainder" or row[0] == "" or row[6] == "Current Exchange Rate":
            break
        data.append({
            "category": row[0],
            "isCompleted": True if row[1] == "TRUE" else False,
            "amount": row[2],
            "account": row[3],
            "notes": row[3],
        })
        
    data = sorted(data, key=lambda x: x['isCompleted'])

        
    
    return {"monthly_budget_data": data}