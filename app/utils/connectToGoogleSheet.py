import base64
import json
import os
from pathlib import Path
import gspread
import traceback
from google.oauth2.service_account import Credentials

def connect_to_google_sheet(sheet_name: str, work_sheet_name: str):
    try:
        encoded_creds = os.getenv("GOOGLE_CREDS_BASE64")
        if not encoded_creds:
            raise RuntimeError("Missing GOOGLE_CREDS_BASE64 env var")

        service_account_info = json.loads(base64.b64decode(encoded_creds))
        scopes = ["https://www.googleapis.com/auth/spreadsheets", 
                "https://www.googleapis.com/auth/drive"]

        creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
        client = gspread.authorize(creds)
        if not client:
            raise RuntimeError("Failed to authorize Google Sheets client")
        sheet = client.open(sheet_name).worksheet(work_sheet_name)
        if not sheet:
            raise ValueError(f"Worksheet '{work_sheet_name}' not found in sheet '{sheet_name}'")
        return sheet

    except Exception as e:
        print(f"Failed to connect to Google Sheet: {e}")
        print(traceback.format_exc())
        return None
