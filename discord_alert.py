import json
import os
from pathlib import Path

import requests


DISCORD_WEBHOOK_URL = os.getenv(
    "DISCORD_WEBHOOK_URL"
)

MAX_MESSAGE_LENGTH = 1900


def split_message(text):

    text = str(text or "")

    if not text:
        return []

    chunks = []

    while len(text) > MAX_MESSAGE_LENGTH:

        split_at = text.rfind(
            "\n",
            0,
            MAX_MESSAGE_LENGTH
        )

        if split_at <= 0:
            split_at = MAX_MESSAGE_LENGTH

        chunks.append(
            text[:split_at]
        )

        text = text[split_at:].lstrip()

    if text:
        chunks.append(text)

    return chunks


def send_discord_message(
    message
):

    if not DISCORD_WEBHOOK_URL:
        raise RuntimeError(
            "DISCORD_WEBHOOK_URL is missing"
        )

    chunks = split_message(
        message
    )

    if not chunks:
        return True

    for chunk in chunks:

        payload = {
            "content": chunk,
            "allowed_mentions": {
                "parse": []
            }
        }

        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json=payload,
            timeout=20
        )

        response.raise_for_status()

    return True


def send_discord_chart(
    image_path,
    message=""
):

    if not DISCORD_WEBHOOK_URL:
        raise RuntimeError(
            "DISCORD_WEBHOOK_URL is missing"
        )

    image_path = Path(
        image_path
    )

    if not image_path.exists():
        raise FileNotFoundError(
            f"Chart not found: {image_path}"
        )

    chunks = split_message(
        message
    )

    first_message = (
        chunks[0]
        if chunks
        else ""
    )

    payload = {
        "allowed_mentions": {
            "parse": []
        }
    }

    if first_message:
        payload["content"] = (
            first_message
        )

    with open(
        image_path,
        "rb"
    ) as image_file:

        files = {
            "files[0]": (
                image_path.name,
                image_file,
                "image/png"
            )
        }

        data = {
            "payload_json":
                json.dumps(
                    payload
                )
        }

        response = requests.post(
            DISCORD_WEBHOOK_URL,
            data=data,
            files=files,
            timeout=30
        )

        response.raise_for_status()

    # If caption was longer than Discord
    # message limit, send remaining parts.
    for chunk in chunks[1:]:

        send_discord_message(
            chunk
        )

    return True
