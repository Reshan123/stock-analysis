from app.utils.connectToGoogleSheet import connect_to_google_sheet

def get_basic_info():
    net_worth_sheet = connect_to_google_sheet("Financial Overview", "Net Worth")
    if not net_worth_sheet:
        print(f"Failed to connect to Google Sheet. {net_worth_sheet}")
        return {"error": "Failed to connect to Google Sheet."}
    
    records = net_worth_sheet.get_all_values()
    if not records:
        print("No data found in the sheet.")
        return {"error": "No data found in the sheet."}
    
    print(f"Fetched {len(records)-1} records from the sheet.")
    basic_info = {}
    for idx, row in enumerate(records[2:], start=2):
        key = row[1].strip()

        if not key:
            continue
            
        basic_info[key] = {
            "type": row[2].strip(),
            "value": row[3].strip(),
            "notes": row[4].strip(),
            "sub_notes": row[5].strip(),
            "row": idx
        }

    sorted_data = {}
    for name, details in basic_info.items():
        # Get the type, or use a default like 'Other' if it's empty
        item_type = details.get("type") or "Other"

        # If this type isn't a key in our new dictionary yet, create it with an empty list
        if item_type not in sorted_data:
            sorted_data[item_type] = []

        # Add the item's name to its details and append it to the correct list
        sorted_data[item_type].append({
            "name": name,
            **details  # Unpacks the rest of the details (value, notes, etc.)
        })

    
    return sorted_data