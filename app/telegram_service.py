import requests
from app.config import TELEGRAM_TOKEN


def send_message(chat_id, text):

    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    requests.post(url, json=payload)
