import requests
from datetime import datetime
from zoneinfo import ZoneInfo


FOREX_FACTORY_JSON = (
    "https://nfs.faireconomy.media/"
    "ff_calendar_thisweek.json"
)

IST = ZoneInfo(
    "Asia/Kolkata"
)

ALLOWED_CURRENCIES = {
    "GBP",
    "EUR",
    "USD",
}

ALLOWED_IMPACTS = {
    "High",
    "Medium",
    "Low",
}


def get_forex_factory_news():

    response = requests.get(
        FOREX_FACTORY_JSON,
        timeout=20,
        headers={
            "User-Agent":
                "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(
        data,
        list
    ):
        raise Exception(
            "Invalid Forex Factory data"
        )

    return data


def parse_event_datetime(
    event
):

    date_value = event.get(
        "date"
    )

    if not date_value:
        return None

    try:

        dt = datetime.fromisoformat(
            date_value
        )

        if dt.tzinfo is None:
            return None

        return dt.astimezone(
            IST
        )

    except Exception:

        return None


def get_today_news():

    data = (
        get_forex_factory_news()
    )

    now_ist = datetime.now(
        IST
    )

    today = now_ist.date()

    events = []

    for event in data:

        currency = event.get(
            "country",
            ""
        ).upper()

        impact = event.get(
            "impact",
            ""
        )

        if (
            currency
            not in ALLOWED_CURRENCIES
        ):
            continue

        if (
            impact
            not in ALLOWED_IMPACTS
        ):
            continue

        event_time = (
            parse_event_datetime(
                event
            )
        )

        if event_time is None:
            continue

        if (
            event_time.date()
            != today
        ):
            continue

        events.append({
            "currency":
                currency,

            "impact":
                impact,

            "title":
                event.get(
                    "title",
                    "Economic Event"
                ),

            "time":
                event_time,

            "forecast":
                event.get(
                    "forecast",
                    ""
                ),

            "previous":
                event.get(
                    "previous",
                    ""
                )
        })

    events.sort(
        key=lambda x:
            x["time"]
    )

    return events


def impact_emoji(
    impact
):

    if impact == "High":
        return "🔴"

    if impact == "Medium":
        return "🟠"

    return "🟡"


def currency_emoji(
    currency
):

    emojis = {
        "GBP": "🇬🇧",
        "EUR": "🇪🇺",
        "USD": "🇺🇸",
    }

    return emojis.get(
        currency,
        "🌍"
    )


def format_news_message():

    events = (
        get_today_news()
    )

    today = datetime.now(
        IST
    )

    header = (
        "📰 TODAY FOREX NEWS\n\n"
        f"📅 {today.strftime('%d %b %Y')}\n"
        "⏰ Time: IST\n"
    )

    if not events:

        return (
            header
            +
            "\n✅ No GBP / EUR / USD "
            "High, Medium or Low "
            "impact news today."
        )

    sections = []

    for currency in [
        "GBP",
        "EUR",
        "USD"
    ]:

        currency_events = [
            event
            for event in events
            if event["currency"]
            == currency
        ]

        if not currency_events:
            continue

        section = (
            f"\n"
            f"{currency_emoji(currency)} "
            f"{currency}\n"
        )

        for event in (
            currency_events
        ):

            time_text = (
                event["time"]
                .strftime(
                    "%I:%M %p"
                )
            )

            emoji = impact_emoji(
                event["impact"]
            )

            section += (
                f"{emoji} "
                f"{time_text} — "
                f"{event['title']}\n"
            )

            if (
                event["forecast"]
                or
                event["previous"]
            ):

                section += (
                    f"   Forecast: "
                    f"{event['forecast'] or '-'}"
                    f" | Previous: "
                    f"{event['previous'] or '-'}\n"
                )

        sections.append(
            section
        )

    return (
        header
        +
        "".join(
            sections
        )
    )


if __name__ == "__main__":

    print(
        format_news_message()
    )
