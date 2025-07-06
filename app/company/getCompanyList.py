from app.utils.telegram import send_telegram_message
from pathlib import Path

async def get_company_list(chat_id: int):
    try:
        file_path = Path(__file__).resolve().parent / "companyList.txt"
        with open(file_path, "r") as f:
            company_list = f.read().splitlines()

        if not company_list:
            send_telegram_message(chat_id, "<b>No companies in the list.</b>")
        else:
            formatted_list = "\n".join([f"<code>{symbol}</code>" for symbol in company_list])
            send_telegram_message(chat_id, f"<b>Company List:</b>\n{formatted_list}")

        return {"ok": True}
    except FileNotFoundError:
        send_telegram_message(chat_id, "<b>Error:</b> company list file not found.")
        return {"error": "File not found"}