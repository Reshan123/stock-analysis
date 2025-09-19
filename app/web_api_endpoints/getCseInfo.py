from app.utils.connectToGoogleSheet import connect_to_google_sheet
import re

def get_cse_info():
    pattern = re.compile(r"^[A-Z]{3,}\.N\d{4}$")
    cse_sheet = connect_to_google_sheet("Financial Overview", "CSE")
    if not cse_sheet:
        print(f"Failed to connect to Google Sheet. {cse_sheet}")
        return {"error": "Failed to connect to Google Sheet."}
    
    cse_records = cse_sheet.get_all_values()
    if not cse_records:
        print("No data found in the sheet.")
        return {"error": "No data found in the sheet."}
    
    companies = []
    for idx, row in enumerate(cse_records[1:], start=2):
        stock_symbol = ""
        if pattern.match(row[2].strip()):
            stock_symbol = row[2].strip()
        elif row[2].strip() == "Actual Cost":
            continue
        else:
            continue

        if stock_symbol == "":
            continue
        
        companies.append({
            "row": idx,
            "stock_symbol": stock_symbol,
            "actual_cost": row[3].strip(),
            "number_of_shares": row[4].strip(),
            "per_share_value": row[5].strip(),
            "current_value": row[6].strip(),
            "gain_loss": row[7].strip(),
        })
    return {"companies": companies}