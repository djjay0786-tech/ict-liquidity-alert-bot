import pandas as pd
from datetime import time
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

    df = df.sort_values("datetime")
    df = df.reset_index(drop=True)

    return df


def get_session_candles(df, session_name, date=None):

    session = SESSIONS[session_name]

    timezone = ZoneInfo(session["timezone"])

    local_df = df.copy()

    # Convert UTC -> session local timezone
    local_df["local_time"] = (
        local_df["datetime"]
        .dt.tz_convert(timezone)
    )

    local_df["local_date"] = (
        local_df["local_time"].dt.date
    )

    local_df["local_clock"] = (
        local_df["local_time"].dt.time
    )

    if date is None:
        date = local_df["local_date"].iloc[-1]

    result = local_df[
        (local_df["local_date"] == date) &
        (local_df["local_clock"] >= session["start"]) &
        (local_df["local_clock"] < session["end"])
    ]

    return result


def calculate_session_levels(df, session_name, date=None):

    session_df = get_session_candles(
        df,
        session_name,
        date
    )

    if session_df.empty:
        return None

    return {
        "session": session_name,
        "date": str(
            session_df["local_date"].iloc[0]
        ),
        "high": float(
            session_df["high"].max()
        ),
        "low": float(
            session_df["low"].min()
        ),
    }


def detect_session_liquidity_grab(
    df,
    session_name
):

    levels = calculate_session_levels(
        df,
        session_name
    )

    if not levels:
        return []

    latest = df.iloc[-1]

    alerts = []

    # Sweep session LOW
    if latest["low"] < levels["low"]:

        alerts.append({
            "type": "BULLISH SESSION LIQUIDITY GRAB",
            "session": session_name,
            "level": "SESSION LOW",
            "liquidity": levels["low"],
            "grab_price": float(latest["low"]),
            "time": str(latest["datetime"]),
        })

    # Sweep session HIGH
    if latest["high"] > levels["high"]:

        alerts.append({
            "type": "BEARISH SESSION LIQUIDITY GRAB",
            "session": session_name,
            "level": "SESSION HIGH",
            "liquidity": levels["high"],
            "grab_price": float(latest["high"]),
            "time": str(latest["datetime"]),
        })

    return alerts


def format_session_alert(symbol, alert):

    emoji = (
        "🟢"
        if "BULLISH" in alert["type"]
        else "🔴"
    )

    return (
        f"{emoji} SESSION LIQUIDITY GRAB\n\n"
        f"Symbol: {symbol}\n"
        f"Session: {alert['session']}\n"
        f"Type: {alert['type']}\n"
        f"Level: {alert['level']}\n"
        f"Liquidity: {alert['liquidity']:.5f}\n"
        f"Grab Price: {alert['grab_price']:.5f}\n"
        f"Time: {alert['time']}"
          )
