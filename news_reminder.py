import json
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from forex_news import (
    get_forex_factory_news,
    parse_event_datetime,
)
from telegram_alert import (
    send_telegram_message,
)


IST = ZoneInfo("Asia/Kolkata")

ALLOWED_CURRENCIES = {
    "GBP",
    "EUR",
    "USD",
}

REMINDER_MINUTES = 12
WINDOW_MINUTES = 5

STATE_FILE = Path(
    "news_state.json"
)


def load_state():

    if not STATE_FILE.exists():
        return {}

    try:

        with open(
            STATE_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    except Exception:

        return {}


def save_state(state):

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            state,
            file,
            indent=2,
        )


def make_event_id(
    currency,
    title,
    event_time,
):

    return (
        f"{currency}|"
        f"{title}|"
        f"{event_time.isoformat()}"
    )


def already_sent(
    event_id,
):

    state = load_state()

    return event_id in state


def mark_sent(
    event_id,
    event,
):

    state = load_state()

    state[event_id] = {
        "currency":
            event["currency"],

        "title":
            event["title"],

        "news_time":
            event["time"].isoformat(),

        "sent_at":
            datetime.now(
                IST
            ).isoformat(),
    }

    save_state(
        state
    )


def get_upcoming_red_news():

    data = (
        get_forex_factory_news()
    )

    now = datetime.now(
        IST
    )

    alerts = []

    for event in data:

        currency = event.get(
            "country",
            "",
        ).upper()

        impact = event.get(
            "impact",
            "",
        )

        if (
            currency
            not in ALLOWED_CURRENCIES
        ):
            continue

        if impact != "High":
            continue

        event_time = (
            parse_event_datetime(
                event
            )
        )

        if event_time is None:
            continue

        target_time = (
            event_time
            -
            timedelta(
                minutes=REMINDER_MINUTES
            )
        )

        if (
            target_time
            <= now
            <
            target_time
            +
            timedelta(
                minutes=WINDOW_MINUTES
            )
        ):

            alerts.append({
                "currency":
                    currency,

                "title":
                    event.get(
                        "title",
                        "Economic Event",
                    ),

                "time":
                    event_time,
            })

    return alerts


def get_pairs(
    currency,
):

    if currency == "USD":

        return (
            "EUR/USD • "
            "GBP/USD • DXY"
        )

    if currency == "EUR":

        return "EUR/USD"

    if currency == "GBP":

        return "GBP/USD"

    return "-"


def format_reminder(
    event,
):

    event_time = (
        event["time"]
        .strftime(
            "%I:%M %p"
        )
    )

    return (
        "🚨 RED NEWS ALERT 🚨\n\n"

        f"Currency: "
        f"{event['currency']}\n\n"

        f"🔴 "
        f"{event['title']}\n\n"

        f"⏰ News Time: "
        f"{event_time} IST\n"

        f"⚠️ "
        f"12 MINUTES TO NEWS\n\n"

        f"📊 Watch: "
        f"{get_pairs(event['currency'])}"
    )


def run_news_reminder():

    events = (
        get_upcoming_red_news()
    )

    if not events:

        print(
            "No High Impact news "
            "inside reminder window."
        )

        return

    for event in events:

        event_id = make_event_id(
            event["currency"],
            event["title"],
            event["time"],
        )

        if already_sent(
            event_id
        ):

            print(
                "Duplicate skipped:",
                event["currency"],
                event["title"],
            )

            continue

        message = (
            format_reminder(
                event
            )
        )

        # State is marked only after
        # Telegram send succeeds.
        send_telegram_message(
            message
        )

        mark_sent(
            event_id,
            event,
        )

        print(
            "Reminder sent:",
            event["currency"],
            event["title"],
        )


if __name__ == "__main__":

    run_news_reminder()
