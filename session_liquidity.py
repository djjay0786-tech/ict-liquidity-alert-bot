import pandas as pd
from datetime import time
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


def _prepare(df):

    if df is None or df.empty:
        return df

    data = df.copy()

    data["datetime"] = pd.to_datetime(
        data["datetime"],
        utc=True
    )

    for column in [
        "open",
        "high",
        "low",
        "close"
    ]:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    data = data.dropna(
        subset=[
            "datetime",
            "high",
            "low"
        ]
    )

    data = data.sort_values(
        "datetime"
    )

    data = data.reset_index(
        drop=True
    )

    return data


def get_completed_sessions(
    df,
    session_name
):

    """
    Returns completed session ranges.

    Session boundaries are calculated
    using the session's local timezone,
    so London / New York DST is handled
    automatically.
    """

    if session_name not in SESSIONS:
        return []

    data = _prepare(df)

    if data is None or data.empty:
        return []

    config = SESSIONS[
        session_name
    ]

    timezone = ZoneInfo(
        config["timezone"]
    )

    local_times = (
        data["datetime"]
        .dt.tz_convert(
            timezone
        )
    )

    data = data.copy()

    data["local_date"] = (
        local_times.dt.date
    )

    data["local_time"] = (
        local_times.dt.time
    )

    session_rows = data[
        (
            data["local_time"]
            >= config["open"]
        )
        &
        (
            data["local_time"]
            < config["close"]
        )
    ]

    if session_rows.empty:
        return []

    latest_utc = data.iloc[-1][
        "datetime"
    ]

    completed = []

    for (
        session_date,
        group
    ) in session_rows.groupby(
        "local_date"
    ):

        close_local = pd.Timestamp(
            year=session_date.year,
            month=session_date.month,
            day=session_date.day,
            hour=config["close"].hour,
            minute=config["close"].minute,
            tz=timezone
        )

        close_utc = (
            close_local.tz_convert(
                "UTC"
            )
        )

        if latest_utc < close_utc:
            continue

        completed.append({
            "session":
                session_name,

            "date":
                str(session_date),

            "high":
                float(
                    group["high"].max()
                ),

            "low":
                float(
                    group["low"].min()
                ),

            "close_time":
                str(close_utc)
        })

    completed.sort(
        key=lambda x: x[
            "close_time"
        ]
    )

    return completed


def get_last_completed_session(
    df,
    session_name
):

    sessions = get_completed_sessions(
        df,
        session_name
    )

    if not sessions:
        return None

    return sessions[-1]


def detect_session_liquidity(
    df,
    session_name
):

    """
    Detect a sweep of the latest
    completed session High / Low.

    The sweep candle must occur AFTER
    that session has closed.

    No candle-close confirmation
    is required.
    """

    data = _prepare(df)

    if data is None or data.empty:
        return []

    session = (
        get_last_completed_session(
            data,
            session_name
        )
    )

    if session is None:
        return []

    latest = data.iloc[-1]

    latest_time = latest[
        "datetime"
    ]

    close_time = pd.to_datetime(
        session["close_time"],
        utc=True
    )

    if latest_time < close_time:
        return []

    session_high = float(
        session["high"]
    )

    session_low = float(
        session["low"]
    )

    latest_high = float(
        latest["high"]
    )

    latest_low = float(
        latest["low"]
    )

    alerts = []

    # Session LOW swept
    if latest_low < session_low:

        alerts.append({
            "type":
                "BULLISH LIQUIDITY GRAB",

            "source":
                session_name,

            "level":
                f"{session_name} LOW",

            "session_date":
                session["date"],

            "liquidity":
                session_low,

            "price":
                latest_low,

            "time":
                str(latest_time)
        })

    # Session HIGH swept
    if latest_high > session_high:

        alerts.append({
            "type":
                "BEARISH LIQUIDITY GRAB",

            "source":
                session_name,

            "level":
                f"{session_name} HIGH",

            "session_date":
                session["date"],

            "liquidity":
                session_high,

            "price":
                latest_high,

            "time":
                str(latest_time)
        })

    return alerts


def format_session_alert(
    symbol,
    alert
):

    if (
        alert["type"]
        == "BULLISH LIQUIDITY GRAB"
    ):
        emoji = "🟢"
    else:
        emoji = "🔴"

    return (
        f"{emoji} SESSION "
        f"LIQUIDITY GRAB\n\n"

        f"Symbol: {symbol}\n"

        f"Source: "
        f"{alert['source']}\n"

        f"Level: "
        f"{alert['level']}\n"

        f"Session Date: "
        f"{alert['session_date']}\n\n"

        f"Liquidity: "
        f"{alert['liquidity']:.5f}\n"

        f"Sweep Price: "
        f"{alert['price']:.5f}\n\n"

        f"Time: "
        f"{alert['time']}"
    )
