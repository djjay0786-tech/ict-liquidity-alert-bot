import os
import requests

from discord_alert import (
    send_discord_message
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


TELEGRAM_URL = (
    f"https://api.telegram.org/"
    f"bot{BOT_TOKEN}/sendMessage"
)


MAX_MESSAGE_LENGTH = 3900


def split_message(message):

    if len(message) <= MAX_MESSAGE_LENGTH:
        return [message]

    parts = []

    current = ""

    for line in message.splitlines(
        keepends=True
    ):

        if (
            len(current)
            +
            len(line)
            >
            MAX_MESSAGE_LENGTH
        ):

            if current:

                parts.append(
                    current.rstrip()
                )

            current = line

        else:

            current += line

    if current:

        parts.append(
            current.rstrip()
        )

    return parts


def send_to_chat(
    chat_id,
    message
):

    if not chat_id:
        return []

    message_parts = split_message(
        message
    )

    results = []

    total_parts = len(
        message_parts
    )

    for index, part in enumerate(
        message_parts,
        start=1
    ):

        if total_parts > 1:

            text = (
                f"📄 Part "
                f"{index}/{total_parts}\n\n"
                f"{part}"
            )

        else:

            text = part

        payload = {
            "chat_id": chat_id,
            "text": text
        }

        response = requests.post(
            TELEGRAM_URL,
            json=payload,
            timeout=20
        )

        try:

            data = response.json()

        except Exception:

            data = {}

        if not response.ok:

            description = data.get(
                "description",
                response.text
            )

            raise Exception(
                f"Telegram error "
                f"{response.status_code}: "
                f"{description}"
            )

        if not data.get(
            "ok",
            False
        ):

            raise Exception(
                data.get(
                    "description",
                    "Telegram API error"
                )
            )

        results.append(
            data
        )

    return results


def send_discord_safe(
    message
):

    # Discord is optional.
    # Telegram must continue working
    # even if Discord has a problem.

    if not os.getenv(
        "DISCORD_WEBHOOK_URL"
    ):
        return False

    try:

        send_discord_message(
            message
        )

        print(
            "✅ Discord alert sent"
        )

        return True

    except Exception as e:

        print(
            "⚠️ Discord alert failed: "
            f"{e}"
        )

        return False


def send_telegram_message(
    message,
    include_discord=True
):

    if not BOT_TOKEN:

        raise Exception(
            "Telegram bot token "
            "not configured"
        )

    chat_ids = []

    if PERSONAL_CHAT_ID:

        chat_ids.append(
            PERSONAL_CHAT_ID
        )

    if (
        GROUP_CHAT_ID
        and
        GROUP_CHAT_ID
        not in chat_ids
    ):

        chat_ids.append(
            GROUP_CHAT_ID
        )

    if not chat_ids:

        raise Exception(
            "No Telegram chat IDs "
            "configured"
        )

    all_results = []

    for chat_id in chat_ids:

        results = send_to_chat(
            chat_id,
            message
        )

        all_results.extend(
            results
        )

    # Send same alert to Discord
    # only after Telegram succeeds.
    if include_discord:

        send_discord_safe(
            message
        )

    return all_results


def send_alert(
    message
):

    return send_telegram_message(
        message,
        include_discord=True
    )
