import pandas as pd
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo


SESSIONS = {
    "ASIA": {
        "timezone": "Asia/Tokyo",
        "start": time(0, 0),
        "end": time(9, 0),
    },

    "LONDON": {
        "timezone": "Europe/London",
        "start": time(8, 0),
        "end": time(17, 0),
    },

    "NEW YORK": {
        "timezone": "America/New_York",
        "start": time(8, 0),
        "end": time(17, 0),
    },
}


def prepare_candles(values):

    df = pd.DataFrame(values)

    if df.empty:
        return df

    df["datetime"] = pd.to_datetime(
        df["datetime"],
        utc=True
    )

    for col in ["open", "high", "low", "close"]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = df.dropna(
        subset=["datetime", "high", "low"]
    )

    df = df.sort_values("datetime")
    df = df.reset_index(drop=True)

    return df


def get_session_range(
    df,
    session_name,
    session_date
):

    session = SESSIONS[session_name]

    tz = ZoneInfo(session["timezone"])

    start_local = datetime.combine(
        session_date,
        session["start"]
    ).replace(tzinfo=tz)

    end_local = datetime.combine(
        session_date,
        session["end"]
    ).replace(tzinfo=tz)

    start_utc = start_local.astimezone(
        ZoneInfo("UTC")
    )

    end_utc = end_local.astimezone(
        ZoneInfo("UTC")
    )

    session_df = df[
        (df["datetime"] >= start_utc) &
        (df["datetime"] < end_utc)
    ]

    if session_df.empty:
        return None

    return {
        "session": session_name,
        "date": str(session_date),
        "high": float(session_df["high"].max()),
        "low": float(session_df["low"].min()),
    }


def get_previous_session_levels(
    df,
    current_time,
    session_name
):

    session = SESSIONS[session_name]

    tz = ZoneInfo(session["timezone"])

    current_local = current_time.astimezone(tz)

    current_date = current_local.date()

    # Check today and previous few days
    for days_back in range(0, 5):

        check_date = (
            current_date -
            timedelta(days=days_back)
        )

        levels = get_session_range(
            df,
            session_name,
            check_date
        )

        if levels:

            session_end = datetime.combine(
                check_date,
                session["end"]
            ).replace(tzinfo=tz)

            session_end_utc = session_end.astimezone(
                ZoneInfo("UTC")
            )

            # Session must already be completed
            if session_end_utc < current_time:

                return levels

    return None


def detect_session_liquidity(
    df,
    current_session
):

    if df.empty:
        return []

    latest = df.iloc[-1]

    current_time = latest["datetime"]

    alerts = []

    # ==================================================
    # 1. ASIA LIQUIDITY → USED DURING LONDON
    # ==================================================

    if current_session == "LONDON":

        asia = get_previous_session_levels(
            df,
            current_time,
            "ASIA"
        )

        if asia:

            if latest["low"] < asia["low"]:

                alerts.append({
                    "type": "BULLISH LIQUIDITY GRAB",
                    "source": "ASIA",
                    "level": "ASIA LOW",
                    "liquidity": asia["low"],
                    "grab_price": float(
                        latest["low"]
                    ),
                    "time": str(
                        latest["datetime"]
                    ),
                })

            if latest["high"] > asia["high"]:

                alerts.append({
                    "type": "BEARISH LIQUIDITY GRAB",
                    "source": "ASIA",
                    "level": "ASIA HIGH",
                    "liquidity": asia["high"],
                    "grab_price": float(
                        latest["high"]
                    ),
                    "time": str(
                        latest["datetime"]
                    ),
                )

    # ==================================================
    # 2. LONDON LIQUIDITY → USED DURING NEW YORK
    # ==================================================

    if current_session == "NEW YORK":

        london = get_previous_session_levels(
            df,
            current_time,
            "LONDON"
        )

        if london:

            if latest["low"] < london["low"]:

                alerts.append({
                    "type": "BULLISH LIQUIDITY GRAB",
                    "source": "LONDON",
                    "level": "LONDON LOW",
                    "liquidity": london["low"],
                    "grab_price": float(
                        latest["low"]
                    ),
                    "time": str(
                        latest["datetime"]
                    ),
                })

            if latest["high"] > london["high"]:

                alerts.append({
                    "type": "BEARISH LIQUIDITY GRAB",
                    "source": "LONDON",
                    "level": "LONDON HIGH",
                    "liquidity": london["high"],
                    "grab_price": float(
                        latest["high"]
                    ),
                    "time": str(
                        latest["datetime"]
                    ),
                )

    return alerts


def format_session_alert(
    symbol,
    alert
):

    emoji = (
        "🟢"
        if "BULLISH" in alert["type"]
        else "🔴"
    )

    return (
        f"{emoji} LIQUIDITY GRAB\n\n"
        f"Symbol: {symbol}\n"
        f"Source: {alert['source']}\n"
        f"Level: {alert['level']}\n"
        f"Liquidity: "
        f"{alert['liquidity']:.5f}\n"
        f"Grab Price: "
        f"{alert['grab_price']:.5f}\n"
        f"Time: {alert['time']}"
    )
