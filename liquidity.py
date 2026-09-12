import pandas as pd


def prepare_candles(values):
    """
    Twelve Data candles -> pandas DataFrame
    """

    df = pd.DataFrame(values)

    if df.empty:
        return df

    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)

    for col in ["open", "high", "low", "close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values("datetime").reset_index(drop=True)

    return df


def previous_day_levels(df):
    """
    Previous Day High / Low
    """

    df = df.copy()

    df["date"] = df["datetime"].dt.date

    daily = df.groupby("date").agg(
        day_high=("high", "max"),
        day_low=("low", "min")
    )

    if len(daily) < 2:
        return None

    previous = daily.iloc[-2]

    return {
        "PDH": float(previous["day_high"]),
        "PDL": float(previous["day_low"])
    }


def current_day_levels(df):
    """
    Current Day High / Low
    """

    today = df["datetime"].dt.date.iloc[-1]

    today_df = df[df["datetime"].dt.date == today]

    if today_df.empty:
        return None

    return {
        "DH": float(today_df["high"].max()),
        "DL": float(today_df["low"].min())
    }


def detect_liquidity_grab(df):
    """
    Detect liquidity sweep/grab.

    Bullish liquidity grab:
    Price goes below liquidity level.

    Bearish liquidity grab:
    Price goes above liquidity level.
    """

    if len(df) < 3:
        return []

    levels = previous_day_levels(df)

    if not levels:
        return []

    latest = df.iloc[-1]

    alerts = []

    # =========================
    # PREVIOUS DAY LOW
    # =========================

    if latest["low"] < levels["PDL"]:
        alerts.append({
            "type": "BULLISH LIQUIDITY GRAB",
            "level": "Previous Day Low",
            "price": float(latest["low"]),
            "liquidity": levels["PDL"],
            "time": str(latest["datetime"])
        })

    # =========================
    # PREVIOUS DAY HIGH
    # =========================

    if latest["high"] > levels["PDH"]:
        alerts.append({
            "type": "BEARISH LIQUIDITY GRAB",
            "level": "Previous Day High",
            "price": float(latest["high"]),
            "liquidity": levels["PDH"],
            "time": str(latest["datetime"])
        })

    return alerts


def format_alert(symbol, alert):

    direction = alert["type"]

    emoji = "🟢" if "BULLISH" in direction else "🔴"

    message = (
        f"{emoji} LIQUIDITY GRAB\n\n"
        f"Symbol: {symbol}\n"
        f"Type: {direction}\n"
        f"Level: {alert['level']}\n"
        f"Liquidity: {alert['liquidity']:.5f}\n"
        f"Grab Price: {alert['price']:.5f}\n"
        f"Time: {alert['time']}"
    )

    return message
