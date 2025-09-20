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
    
    companies = {
        "personal": [],
        "dads": []
    }

    # Track if we’re before or after the "Total" row
    before_total = True

    for idx, row in enumerate(cse_records[1:], start=2):  # skip header row
        if "Total" in row[1]:  # assume first column marks the total row
            before_total = False
            continue

        stock_symbol = ""
        if len(row) > 2 and pattern.match(row[2].strip()):
            stock_symbol = row[2].strip()
        elif len(row) > 2 and row[2].strip() == "Actual Cost":
            continue
        else:
            continue

        if stock_symbol == "":
            continue
        
        stock_data = {
            "row": idx,
            "stock_symbol": stock_symbol,
            "actual_cost": row[3].strip(),
            "number_of_shares": row[4].strip(),
            "per_share_value": row[5].strip(),
            "current_value": row[6].strip(),
            "gain_loss": row[7].strip(),
        }

        if before_total:
            companies["personal"].append(stock_data)
        else:
            companies["dads"].append(stock_data)

    return {"companies": companies}
