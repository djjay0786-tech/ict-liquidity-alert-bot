import pandas as pd


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
# PREVIOUS DAY HIGH / LOW
# ============================================================

def previous_day_levels(df):

    if df.empty:
        return None

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


# ============================================================
# CURRENT DAY HIGH / LOW
# ============================================================

def current_day_levels(df):

    if df.empty:
        return None

    today = df["datetime"].dt.date.iloc[-1]

    today_df = df[
        df["datetime"].dt.date == today
    ]

    if today_df.empty:
        return None

    return {
        "DH": float(today_df["high"].max()),
        "DL": float(today_df["low"].min())
    }


# ============================================================
# DETECT PREVIOUS DAY LIQUIDITY GRAB
# ============================================================

def detect_liquidity_grab(df):

    if len(df) < 3:
        return []

    levels = previous_day_levels(df)

    if levels is None:
        return []

    latest = df.iloc[-1]

    alerts = []


    # ========================================================
    # PREVIOUS DAY LOW SWEEP
    # ========================================================

    if latest["low"] < levels["PDL"]:

        alerts.append({

            "type": "BULLISH LIQUIDITY GRAB",

            "level": "Previous Day Low",

            "price": float(
                latest["low"]
            ),

            "liquidity": levels["PDL"],

            "time": str(
                latest["datetime"]
            )

        })


    # ========================================================
    # PREVIOUS DAY HIGH SWEEP
    # ========================================================

    if latest["high"] > levels["PDH"]:

        alerts.append({

            "type": "BEARISH LIQUIDITY GRAB",

            "level": "Previous Day High",

            "price": float(
                latest["high"]
            ),

            "liquidity": levels["PDH"],

            "time": str(
                latest["datetime"]
            )

        })


    return alerts


# ============================================================
# FORMAT ALERT
# ============================================================

def format_alert(symbol, alert):

    if "BULLISH" in alert["type"]:

        emoji = "🟢"

    else:

        emoji = "🔴"


    message = (

        f"{emoji} LIQUIDITY GRAB\n\n"

        f"Symbol: {symbol}\n"

        f"Type: {alert['type']}\n"

        f"Level: {alert['level']}\n"

        f"Liquidity: "
        f"{alert['liquidity']:.5f}\n"

        f"Grab Price: "
        f"{alert['price']:.5f}\n"

        f"Time: {alert['time']}"

    )

    return message
