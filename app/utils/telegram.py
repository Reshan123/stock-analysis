import requests
import re
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_telegram_message(chat_id: int, text: str):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

def markdown_to_telegram_html(markdown_text: str) -> str:
    markdown_text = re.sub(r"</?think>", "", markdown_text).strip()
    markdown_text = markdown_text.replace("\n", "<br>")
    return markdown_text

def clean_telegram_html(text: str) -> str:
    allowed_tags = ["b", "i", "u", "s", "code", "pre", "a"]
    return re.sub(r"</?(?!(" + "|".join(allowed_tags) + r"))[^>]+>", "", text)
