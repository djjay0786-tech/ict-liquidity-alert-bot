import pandas as pd
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo


# ============================================================
# SESSION SETTINGS
# ============================================================

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


UTC = ZoneInfo("UTC")


# ============================================================
# PREPARE CANDLES
# ============================================================

def prepare_candles(values):

    df = pd.DataFrame(values)

    if df.empty:
        return df

    df["datetime"] = pd.to_datetime(
        df["datetime"],
        utc=True
    )

    for column in [
        "open",
        "high",
        "low",
        "close"
    ]:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = df.dropna(
        subset=[
            "datetime",
            "high",
            "low"
        ]
    )

    df = df.sort_values(
        "datetime"
    )

    df = df.reset_index(
        drop=True
    )

    return df


# ============================================================
# GET SESSION HIGH / LOW
# ============================================================

def get_session_range(
    df,
    session_name,
    session_date
):

    session = SESSIONS[session_name]

    timezone = ZoneInfo(
        session["timezone"]
    )

    start_local = datetime.combine(
        session_date,
        session["start"]
    ).replace(
        tzinfo=timezone
    )

    end_local = datetime.combine(
        session_date,
        session["end"]
    ).replace(
        tzinfo=timezone
    )

    start_utc = start_local.astimezone(
        UTC
    )

    end_utc = end_local.astimezone(
        UTC
    )

    session_df = df[
        (df["datetime"] >= start_utc)
        &
        (df["datetime"] < end_utc)
    ]

    if session_df.empty:
        return None

    session_high = float(
        session_df["high"].max()
    )

    session_low = float(
        session_df["low"].min()
    )

    return {
        "session": session_name,
        "date": str(session_date),
        "high": session_high,
        "low": session_low,
    }


# ============================================================
# GET LAST COMPLETED SESSION
# ============================================================

def get_previous_session_levels(
    df,
    current_time,
    session_name
):

    session = SESSIONS[session_name]

    timezone = ZoneInfo(
        session["timezone"]
    )

    current_local = current_time.astimezone(
        timezone
    )

    current_date = current_local.date()

    for days_back in range(0, 5):

        check_date = (
            current_date
            - timedelta(days=days_back)
        )

        levels = get_session_range(
            df,
            session_name,
            check_date
        )

        if levels is None:
            continue

        session_end_local = datetime.combine(
            check_date,
            session["end"]
        ).replace(
            tzinfo=timezone
        )

        session_end_utc = (
            session_end_local.astimezone(
                UTC
            )
        )

        if session_end_utc < current_time:

            return levels

    return None


# ============================================================
# DETECT SESSION LIQUIDITY
# ============================================================

def detect_session_liquidity(
    df,
    current_session
):

    if df.empty:
        return []

    latest = df.iloc[-1]

    current_time = latest["datetime"]

    alerts = []


    # ========================================================
    # LONDON SESSION
    # CHECK ASIA HIGH / LOW
    # ========================================================

    if current_session == "LONDON":

        asia = get_previous_session_levels(
            df,
            current_time,
            "ASIA"
        )

        if asia is not None:

            # -----------------------------------------------
            # ASIA LOW SWEEP
            # -----------------------------------------------

            if latest["low"] < asia["low"]:

                alert = {
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
                }

                alerts.append(
                    alert
                )


            # -----------------------------------------------
            # ASIA HIGH SWEEP
            # -----------------------------------------------

            if latest["high"] > asia["high"]:

                alert = {
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
                }

                alerts.append(
                    alert
                )


    # ========================================================
    # NEW YORK SESSION
    # CHECK LONDON HIGH / LOW
    # ========================================================

    if current_session == "NEW YORK":

        london = get_previous_session_levels(
            df,
            current_time,
            "LONDON"
        )

        if london is not None:

            # -----------------------------------------------
            # LONDON LOW SWEEP
            # -----------------------------------------------

            if latest["low"] < london["low"]:

                alert = {
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
                }

                alerts.append(
                    alert
                )


            # -----------------------------------------------
            # LONDON HIGH SWEEP
            # -----------------------------------------------

            if latest["high"] > london["high"]:

                alert = {
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
                }

                alerts.append(
                    alert
                )


    return alerts


# ============================================================
# FORMAT TELEGRAM / CONSOLE ALERT
# ============================================================

def format_session_alert(
    symbol,
    alert
):

    if "BULLISH" in alert["type"]:

        emoji = "🟢"

    else:

        emoji = "🔴"


    message = (
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

    return message
