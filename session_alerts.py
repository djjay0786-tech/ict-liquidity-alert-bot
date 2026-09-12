from datetime import timedelta, time
from zoneinfo import ZoneInfo


SESSIONS = {
    "ASIA": {
        "timezone": "Asia/Tokyo",
        "open": time(0, 0),
        "close": time(9, 0),
    },

    "LONDON": {
        "timezone": "Europe/London",
        "open": time(8, 0),
        "close": time(17, 0),
    },

    "NEW YORK": {
        "timezone": "America/New_York",
        "open": time(8, 0),
        "close": time(17, 0),
    },
}


EVENT_WINDOW_MINUTES = 15


def is_inside_event_window(
    local_time,
    target_time
):

    target = local_time.replace(
        hour=target_time.hour,
        minute=target_time.minute,
        second=0,
        microsecond=0
    )

    difference = (
        local_time - target
    )

    return (
        timedelta(0)
        <= difference
        <
        timedelta(
            minutes=EVENT_WINDOW_MINUTES
        )
    )


def get_session_events(
    current_utc
):

    events = []

    for session_name, session in (
        SESSIONS.items()
    ):

        timezone = ZoneInfo(
            session["timezone"]
        )

        local_time = (
            current_utc.astimezone(
                timezone
            )
        )

        event_date = (
            local_time.date().isoformat()
        )

        if is_inside_event_window(
            local_time,
            session["open"]
        ):

            events.append({
                "session":
                    session_name,

                "event":
                    "OPEN",

                "event_date":
                    event_date,

                "scheduled_time":
                    session[
                        "open"
                    ].strftime("%H:%M"),

                "local_time":
                    str(local_time)
            })

        if is_inside_event_window(
            local_time,
            session["close"]
        ):

            events.append({
                "session":
                    session_name,

                "event":
                    "CLOSE",

                "event_date":
                    event_date,

                "scheduled_time":
                    session[
                        "close"
                    ].strftime("%H:%M"),

                "local_time":
                    str(local_time)
            })

    return events


def format_session_event(
    event
):

    if event["event"] == "OPEN":
        emoji = "🟢"
    else:
        emoji = "🔴"

    return (
        f"{emoji} SESSION "
        f"{event['event']}\n\n"

        f"Session: "
        f"{event['session']}\n"

        f"Event: "
        f"{event['event']}\n"

        f"Scheduled Time: "
        f"{event['scheduled_time']}\n"

        f"Local Time: "
        f"{event['local_time']}"
    )
