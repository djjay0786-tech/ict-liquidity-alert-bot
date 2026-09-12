from datetime import datetime, time
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


def get_session_events(current_utc):
    """
    Return session open/close events
    matching the current UTC time.
    """

    events = []

    for session_name, session in SESSIONS.items():

        timezone = ZoneInfo(
            session["timezone"]
        )

        local_time = current_utc.astimezone(
            timezone
        )

        current_hm = (
            local_time.hour,
            local_time.minute
        )

        open_hm = (
            session["open"].hour,
            session["open"].minute
        )

        close_hm = (
            session["close"].hour,
            session["close"].minute
        )

        if current_hm == open_hm:

            events.append({
                "session": session_name,
                "event": "OPEN",
                "local_time": str(local_time)
            })

        if current_hm == close_hm:

            events.append({
                "session": session_name,
                "event": "CLOSE",
                "local_time": str(local_time)
            })

    return events


def format_session_event(event):

    session = event["session"]
    event_type = event["event"]

    if event_type == "OPEN":
        emoji = "🟢"
    else:
        emoji = "🔴"

    return (
        f"{emoji} SESSION {event_type}\n\n"
        f"Session: {session}\n"
        f"Event: {event_type}\n"
        f"Local Time: {event['local_time']}"
    )
