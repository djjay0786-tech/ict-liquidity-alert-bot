import os
import requests


BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

PERSONAL_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID"
)

GROUP_CHAT_ID = os.getenv(
    "TELEGRAM_GROUP_CHAT_ID"
)


TELEGRAM_URL = (
    f"https://api.telegram.org/"
    f"bot{BOT_TOKEN}/sendMessage"
)


def send_to_chat(
    chat_id,
    message
):

    if not chat_id:
        return None

    payload = {
        "chat_id": chat_id,
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


def send_telegram_message(
    message
):

    if not BOT_TOKEN:
        raise Exception(
            "Telegram bot token "
            "not configured"
        )

    if (
        not PERSONAL_CHAT_ID
        and
        not GROUP_CHAT_ID
    ):
        raise Exception(
            "No Telegram chat IDs "
            "configured"
        )

    results = []

    if PERSONAL_CHAT_ID:

        personal_result = (
            send_to_chat(
                PERSONAL_CHAT_ID,
                message
            )
        )

        results.append({
            "destination":
                "personal",
            "result":
                personal_result
        })

    if GROUP_CHAT_ID:

        group_result = (
            send_to_chat(
                GROUP_CHAT_ID,
                message
            )
        )

        results.append({
            "destination":
                "group",
            "result":
                group_result
        })

    return results


def send_alert(
    message
):

    return send_telegram_message(
        message
    )
