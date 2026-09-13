import os
from pathlib import Path

import requests

from telegram_alert import (
    send_telegram_message
)

from tradingview_link import (
    add_tradingview_link
)


BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

PERSONAL_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID"
)

GROUP_CHAT_ID = os.getenv(
    "TELEGRAM_GROUP_CHAT_ID"
)


SEND_PHOTO_URL = (
    f"https://api.telegram.org/"
    f"bot{BOT_TOKEN}/sendPhoto"
)


def get_chat_ids():

    chat_ids = []

    for chat_id in [
        PERSONAL_CHAT_ID,
        GROUP_CHAT_ID
    ]:

        if (
            chat_id
            and chat_id not in chat_ids
        ):
            chat_ids.append(
                chat_id
            )

    return chat_ids


def send_photo_to_chat(
    chat_id,
    chart_path,
    caption
):

    path = Path(
        chart_path
    )

    if not path.exists():

        raise FileNotFoundError(
            f"Chart not found: "
            f"{chart_path}"
        )

    with open(
        path,
        "rb"
    ) as photo:

        response = requests.post(
            SEND_PHOTO_URL,

            data={
                "chat_id":
                    chat_id,

                "caption":
                    caption
            },

            files={
                "photo":
                    photo
            },

            timeout=30
        )

    if not response.ok:

        try:
            description = (
                response.json()
                .get(
                    "description",
                    "Unknown Telegram error"
                )
            )

        except Exception:

            description = (
                response.text
            )

        raise Exception(
            f"Telegram photo error "
            f"{response.status_code}: "
            f"{description}"
        )

    return True


def send_chart_alert(
    chart_path,
    message,
    symbol,
    timeframe
):

    if not BOT_TOKEN:

        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN "
            "not configured"
        )

    chat_ids = (
        get_chat_ids()
    )

    if not chat_ids:

        raise RuntimeError(
            "No Telegram chat ID "
            "configured"
        )

    full_message = (
        add_tradingview_link(
            message,
            symbol,
            timeframe
        )
    )

    # Telegram photo captions have
    # a smaller limit than normal messages.
    # Most ICT alerts should fit here.
    if len(full_message) <= 1000:

        for chat_id in chat_ids:

            send_photo_to_chat(
                chat_id,
                chart_path,
                full_message
            )

        print(
            "📸 Chart + alert sent"
        )

        return True

    # If alert becomes too long:
    # send small chart first,
    # then complete text separately.
    short_caption = (
        f"📈 {symbol} • "
        f"{timeframe}\n"
        f"ICT Alert Chart"
    )

    for chat_id in chat_ids:

        send_photo_to_chat(
            chat_id,
            chart_path,
            short_caption
        )

    send_telegram_message(
        full_message
    )

    print(
        "📸 Chart sent + "
        "full alert sent separately"
    )

    return True
