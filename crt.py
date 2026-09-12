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
            "open",
            "high",
            "low",
            "close"
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
# DETECT CRT
# ============================================================

def detect_crt(df):

    if len(df) < 3:
        return []

    alerts = []

    # Last two COMPLETED candles
    first = df.iloc[-3]
    second = df.iloc[-2]
    third = df.iloc[-1]


    # ========================================================
    # BULLISH CRT
    #
    # 1. First candle LOW is swept
    # 2. Second candle BODY closes above First HIGH
    # 3. Third candle OPEN = Entry reference
    # ========================================================

    bullish_sweep = (
        first["low"] < df.iloc[-4]["low"]
        if len(df) >= 4
        else False
    )

    bullish_confirmation = (
        second["close"] > first["high"]
    )

    if bullish_sweep and bullish_confirmation:

        alerts.append({

            "type": "BULLISH CRT",

            "first_candle_time": str(
                first["datetime"]
            ),

            "second_candle_time": str(
                second["datetime"]
            ),

            "entry_time": str(
                third["datetime"]
            ),

            "first_high": float(
                first["high"]
            ),

            "first_low": float(
                first["low"]
            ),

            "confirmation_close": float(
                second["close"]
            ),

            "entry_price": float(
                third["open"]
            )

        })


    # ========================================================
    # BEARISH CRT
    #
    # 1. First candle HIGH is swept
    # 2. Second candle BODY closes below First LOW
    # 3. Third candle OPEN = Entry reference
    # ========================================================

    bearish_sweep = (
        first["high"] > df.iloc[-4]["high"]
        if len(df) >= 4
        else False
    )

    bearish_confirmation = (
        second["close"] < first["low"]
    )

    if bearish_sweep and bearish_confirmation:

        alerts.append({

            "type": "BEARISH CRT",

            "first_candle_time": str(
                first["datetime"]
            ),

            "second_candle_time": str(
                second["datetime"]
            ),

            "entry_time": str(
                third["datetime"]
            ),

            "first_high": float(
                first["high"]
            ),

            "first_low": float(
                first["low"]
            ),

            "confirmation_close": float(
                second["close"]
            ),

            "entry_price": float(
                third["open"]
            )

        })


    return alerts


# ============================================================
# FORMAT CRT ALERT
# ============================================================

def format_crt_alert(
    symbol,
    timeframe,
    alert
):

    if alert["type"] == "BULLISH CRT":

        emoji = "🟢"

    else:

        emoji = "🔴"


    message = (

        f"{emoji} {alert['type']}\n\n"

        f"Symbol: {symbol}\n"

        f"Timeframe: {timeframe}\n\n"

        f"First Candle High: "
        f"{alert['first_high']:.5f}\n"

        f"First Candle Low: "
        f"{alert['first_low']:.5f}\n\n"

        f"Confirmation Close: "
        f"{alert['confirmation_close']:.5f}\n"

        f"Entry Reference: "
        f"{alert['entry_price']:.5f}\n\n"

        f"Confirmation Time: "
        f"{alert['second_candle_time']}"

    )

    return message
