import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_TOKEN_2 = os.getenv("TELEGRAM_BOT_TOKEN_2", "")

TELEGRAM_API_URL = ""

def send_telegram_message(chat_id: int, text: str, bot_version = 1):
    try:
        if bot_version == 1:
            TELEGRAM_API_URL =  f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
        else:
            TELEGRAM_API_URL =  f"https://api.telegram.org/bot{TELEGRAM_TOKEN_2}"
        payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        }
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

    except Exception as e:
        print(f"Error sending Telegram message: {e}")
