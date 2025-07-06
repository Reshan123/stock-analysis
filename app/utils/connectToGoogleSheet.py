from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials

def connect_to_google_sheet(sheet_name: str):
    try:
        creds_path = Path(__file__).resolve().parent / "credentials" / "credentials.json"
        scopes = ["https://www.googleapis.com/auth/spreadsheets", 
                "https://www.googleapis.com/auth/drive"]

        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open(sheet_name).get_worksheet(1)  
        print(f"Connected to Google Sheet: {sheet_name}")
        return sheet

    except Exception as e:
        print(f"Failed to connect to Google Sheet: {e}")
        return None
