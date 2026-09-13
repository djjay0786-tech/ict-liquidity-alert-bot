import os
from pathlib import Path

import requests

from telegram_alert import (
    send_telegram_message
)

from discord_alert import (
    send_discord_chart
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
            and
            chat_id not in chat_ids
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


def send_discord_chart_safe(
    chart_path,
    message
):

    if not os.getenv(
        "DISCORD_WEBHOOK_URL"
    ):

        return False

    try:

        send_discord_chart(
            chart_path,
            message
        )

        print(
            "📸 Discord chart + "
            "alert sent"
        )

        return True

    except Exception as e:

        # Never break Telegram because
        # Discord had a problem.
        print(
            "⚠️ Discord chart failed: "
            f"{e}"
        )

        return False


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

    # =====================================
    # SHORT ALERT
    # =====================================

    if len(full_message) <= 1000:

        for chat_id in chat_ids:

            send_photo_to_chat(
                chat_id,
                chart_path,
                full_message
            )

        # Discord receives same chart
        # + same TradingView link.
        send_discord_chart_safe(
            chart_path,
            full_message
        )

        print(
            "📸 Chart + alert sent"
        )

        return True

    # =====================================
    # LONG ALERT
    # =====================================

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

    # Telegram full text only.
    # Do NOT send Discord text here,
    # otherwise Discord would get
    # duplicate alert.
    send_telegram_message(
        full_message,
        include_discord=False
    )

    # Discord gets chart + full text.
    send_discord_chart_safe(
        chart_path,
        full_message
    )

    print(
        "📸 Chart sent + "
        "full alert sent separately"
    )

    return True
