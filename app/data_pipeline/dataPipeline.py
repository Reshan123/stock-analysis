import pandas as pd
import io

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
            
            print("Successfully loaded CSV into DataFrame:")
            print(df.head())
    except Exception as e:
        print(f"Error in update_stock_prices: {e}")
        send_telegram_message(
            chat_id=chat_id,  # Replace with your actual chat ID
            text=f"<b>Error updating stock prices: {e}</b>",
            bot_version=bot_version
        )    