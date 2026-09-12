import os
import requests


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TELEGRAM_URL = (
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
)


def send_telegram_message(message):

    if not BOT_TOKEN or not CHAT_ID:
        raise Exception(
            "Telegram credentials not configured"
        )

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(
        TELEGRAM_URL,
        json=payload,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    if not data.get("ok"):
        raise Exception(
            data.get(
                "description",
                "Telegram API error"
            )
        )

    return data


def send_alert(message):
    return send_telegram_message(message)
