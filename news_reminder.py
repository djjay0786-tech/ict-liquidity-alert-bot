from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from forex_news import get_forex_factory_news, parse_event_datetime
from telegram_alert import send_telegram_message


IST = ZoneInfo("Asia/Kolkata")

ALLOWED_CURRENCIES = {
    "GBP",
    "EUR",
    "USD",
}

REMINDER_MINUTES = 12

# Workflow delay सहन करण्यासाठी window
WINDOW_MINUTES = 5


def get_upcoming_red_news():

    data = get_forex_factory_news()

    now = datetime.now(IST)

    alerts = []

    for event in data:

        currency = event.get(
            "country",
            ""
        ).upper()

        impact = event.get(
            "impact",
            ""
        )

        if currency not in ALLOWED_CURRENCIES:
            continue

        if impact != "High":
            continue

        event_time = parse_event_datetime(
            event
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

        # Alert if workflow runs during
        # the 5-minute window after
        # the 12-minute reminder point.
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
                        "Economic Event"
                    ),

                "time":
                    event_time
            })

    return alerts


def get_pairs(currency):

    if currency == "USD":
        return (
            "EUR/USD • GBP/USD • DXY"
        )

    if currency == "EUR":
        return "EUR/USD"

    if currency == "GBP":
        return "GBP/USD"

    return "-"


def format_reminder(event):

    event_time = (
        event["time"]
        .strftime("%I:%M %p")
    )

    return (
        "🚨 RED NEWS ALERT 🚨\n\n"
        f"Currency: "
        f"{event['currency']}\n\n"
        f"🔴 {event['title']}\n\n"
        f"⏰ News Time: "
        f"{event_time} IST\n"
        f"⚠️ 12 MINUTES TO NEWS\n\n"
        f"📊 Watch: "
        f"{get_pairs(event['currency'])}"
    )


def run_news_reminder():

    events = get_upcoming_red_news()

    if not events:
        print(
            "No High Impact news "
            "inside reminder window."
        )
        return

    for event in events:

        message = format_reminder(
            event
        )

        send_telegram_message(
            message
        )

        print(
            "Reminder sent:",
            event["currency"],
            event["title"]
        )


if __name__ == "__main__":
    run_news_reminder()
