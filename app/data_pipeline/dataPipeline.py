import pandas as pd
import io

from app.utils.connectToGoogleSheet import connect_to_google_sheet
from app.utils.connectToGoogleDrive import get_single_drive_file_content
from app.utils.telegram import send_telegram_message

async def data_pipeline(bot_version = 1):
    folder_with_csv = "MyMoney CSV Imports"

    # Get the CSV content from the single file in the folder
    try:
        csv_content = get_single_drive_file_content(folder_with_csv)

        if csv_content:
            csv_file_like_object = io.StringIO(csv_content)
            df = pd.read_csv(csv_file_like_object)
            
            # transform date
            df['TIME'] = pd.to_datetime(df['TIME'])
            df['TIME'] = df['TIME'].dt.strftime('%#m/%#d/%Y')

            print("Successfully loaded CSV into DataFrame:")
            print(df.head())

            sheet_name = "Financial Overview"
            sheet = connect_to_google_sheet(sheet_name, "Sheet17")
            if not sheet:
                print(f"Failed to connect to Google Sheet. {sheet}")
                return
            try:
                # --- 3. Convert DataFrame to a list of lists (without header) ---
                data_to_append = df.values.tolist()
                
                # --- 4. Append the data to the worksheet ---
                sheet.append_rows(data_to_append)
                
                print(f"✅ Success! Appended {len(data_to_append)} rows to 'Sheet17'.")

            except gspread.exceptions.APIError as e:
                print(f"❌ Google API Error: {e}")
            except Exception as e:
                print(f"❌ An unexpected error occurred: {e}")

        
    except Exception as e:
        print(f"Error in update_stock_prices: {e}")
        send_telegram_message(
            chat_id=chat_id,  # Replace with your actual chat ID
            text=f"<b>Error updating stock prices: {e}</b>",
            bot_version=bot_version
        )    