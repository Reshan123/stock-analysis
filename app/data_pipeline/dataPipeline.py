import pandas as pd
import io
import base64
import json
import os

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from app.utils.connectToGoogleSheet import connect_to_google_sheet
from app.utils.archiveDriveFile import archive_drive_file
from app.utils.connectToGoogleDrive import get_single_drive_file_content
from app.utils.telegram import send_telegram_message

async def data_pipeline(chat_id: int, bot_version = 1):
    folder_with_csv = "MyMoney CSV Imports"

    # Get the CSV content from the single file in the folder
    try:
        file_content, file_to_move_id, source_folder_id = get_single_drive_file_content(folder_with_csv)

        if file_content:
            csv_file_like_object = io.StringIO(file_content)
            df = pd.read_csv(csv_file_like_object)
            
            # transform date
            df['TIME'] = pd.to_datetime(df['TIME'])
            df['TIME'] = df['TIME'].dt.strftime('%#m/%#d/%Y')

            # other transforms

            #if category is savings type changed to investments
            df.loc[df['CATEGORY'] == 'Savings', 'TYPE'] = 'Investment'

            # remove mom savings category
            df = df[df['CATEGORY'] != 'Moms savings']

            print("Successfully loaded CSV into DataFrame:")

            sheet_name = "Financial Overview"
            work_sheet_name = "My Money Export"
            sheet = connect_to_google_sheet(sheet_name, work_sheet_name)
            if not sheet:
                print(f"Failed to connect to Google Sheet. {sheet}")
                return
            try:
                # --- 3. Convert DataFrame to a list of lists (without header) ---
                data_to_append = df.values.tolist()
                
                # --- 4. Append the data to the worksheet ---
                sheet.insert_rows(data_to_append, row=3, value_input_option='USER_ENTERED')
                
                print(f"✅ Success! Appended {len(data_to_append)} rows to {work_sheet_name}.")

                if file_to_move_id and source_folder_id:
                    # --- Authentication ---
                    encoded_creds = os.getenv("GOOGLE_CREDS_BASE64")
                    if not encoded_creds:
                        raise RuntimeError("Missing GOOGLE_CREDS_BASE64 env var")

                    service_account_info = json.loads(base64.b64decode(encoded_creds))
                    scopes = ["https://www.googleapis.com/auth/drive"] # Simplified scopes

                    creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
                    drive_service = build('drive', 'v3', credentials=creds)
                    
                    archive_drive_file(drive_service, file_to_move_id, source_folder_id)

            except gspread.exceptions.APIError as e:
                print(f"❌ Google API Error: {e}")
            except Exception as e:
                print(f"❌ An unexpected error occurred: {e}")
        
        send_telegram_message(
            chat_id=chat_id,  # Replace with your actual chat ID
            text=f"<b>✅ Success! Appended {len(data_to_append)} rows to {work_sheet_name}.</b>",
            bot_version=bot_version
        )
    except Exception as e:
        print(f"Error in update_stock_prices: {e}")
        send_telegram_message(
            chat_id=chat_id,  # Replace with your actual chat ID
            text=f"<b>Error updating stock prices: {e}</b>",
            bot_version=bot_version
        )    